import json
import tempfile

from ocr_joplin_notes import rest


class JoplinNote:
    def __init__(self, json_data):
        self.id = json_data.get("id", None)
        self.title = json_data.get("title", None)
        self.body = json_data.get("body", None)
        self.source = json_data.get("source", None)
        self.markup_language = json_data.get("markup_language", None)


class JoplinResource:
    def __init__(self, json_data):
        self.id = json_data.get("id", None)
        self.filename = json_data.get("filename", None)
        self.mime = json_data.get("mime", None)
        self.title = json_data.get("title", None)


class JoplinDataWrapper:

    def __init__(self, server, token):
        self.REST = rest.RestApi(server, token)

    @staticmethod
    def __paginate_by_title(page: int):
        return {'order_by': 'title',
                'limit': '100',
                'page': f"{page}"
                }

    def get_all_tags_from_note(self, note_id: str):
        if note_id is None:
            return None
        res = self.REST.rest_get('/notes/{}/tags'.format(note_id), params={'fields': 'title'})
        tags = res.json()["items"]
        list_of_tags = list([dic.get("title") for dic in tags])
        return list_of_tags

    def is_valid_connection(self):
        try:
            res = self.REST.rest_get('/notes')
            error = res.json()["error"]
            print(error)
            return False
        except KeyError as e:
            return True

    def find_tag_id_by_title(self, title: str, page: int = 1):
        if title is None:
            return None
        res = self.REST.rest_get('/tags', params=self.__paginate_by_title(page))
        tags = res.json()["items"]
        for tag in tags:
            if tag.get("title") == title:
                return tag.get("id")
        if res.json()["has_more"]:
            return self.find_tag_id_by_title(title, page + 1)
        else:
            return None

    def create_tag(self, title):
        tag_id = self.find_tag_id_by_title(title.lower())
        if tag_id is None:
            res = self.REST.rest_post("/tags", data='{{ "title" : {} }}'.format(json.dumps(title)))
            tag_id = res.json()["id"]
        return tag_id

    def delete_tag(self, title):
        tag_id = self.find_tag_id_by_title(title)
        if tag_id is not None:
            res = self.REST.rest_delete("/tags/{}".format(tag_id))
            return res.status_code
        return None

    def tag_note(self, note_id, tag_title):
        tag_id = self.find_tag_id_by_title(tag_title)
        res = self.REST.rest_post("/tags/{}/notes".format(tag_id), data='{{ "id" : {} }}'.format(json.dumps(note_id)))
        return tag_id

    def perform_on_tagged_note_ids(self, usage_function, tag_id, exclude_tags, page: int = 1):
        res = self.REST.rest_get('/tags/{}/notes'.format(tag_id), params=self.__paginate_by_title(page))
        notes = res.json()["items"]
        for note in notes:
            note_id = note.get("id")
            all_tags = self.get_all_tags_from_note(note_id)  # get all tags of the current note
            # check if any tag in the list exclude_tags is equal to any tag of the current notes' tags
            if len(set(exclude_tags).intersection(all_tags)) == 0:
                usage_function(note_id)
            else:
                note = self.get_note_by_id(note_id)
                print(f"------------------------------------\nnote: {note.title}")
                print("Excluding this note\n")
        if res.json()["has_more"]:
            return self.perform_on_tagged_note_ids(usage_function, tag_id, exclude_tags, page + 1)
        else:
            return 0

    def perform_on_all_note_ids(self, usage_function, page: int = 1):
        res = self.REST.rest_get('/notes', params=self.__paginate_by_title(page))
        notes = res.json()["items"]
        for note in notes:
            usage_function(note.get("id"))
        if res.json()["has_more"]:
            return self.perform_on_all_note_ids(usage_function, page + 1)
        else:
            return None

    def get_note_by_id(self, note_id):
        res = self.REST.rest_get('/notes/{}'.format(note_id), params={'fields': 'id,title,body,source,markup_language'})
        return JoplinNote(res.json())

    def update_note_body(self, note_id, new_body: str):
        res = self.REST.rest_put("/notes/{}".format(note_id), values='{{ "body" : {} }}'.format(json.dumps(new_body)))

    def save_resource_to_file(self, resource: JoplinResource):
        file_download = self.REST.rest_get('/resources/{}/file'.format(resource.id), None)
        full_path = tempfile.mktemp(dir=tempfile.tempdir)
        with open(full_path, 'wb') as f:
            f.write(file_download.content)
        return full_path

    def get_note_resources(self, note_id):
        res = self.REST.rest_get("/notes/{}/resources/".format(note_id), None)
        return res.json()["items"]

    def get_resource_by_id(self, resource_id):
        res = self.REST.rest_get('/resources/{}'.format(resource_id), params={'fields': 'id,title,filename,mime'})
        return JoplinResource(res.json())

    def save_preview_image_as_resource(self, note_id, filename: str, title: str):
        with open(filename, "rb") as file:
            props = f'{{"title":"{title}", "filename":"{title}.png"}}'
            files = {
                "data": (json.dumps(filename), file),
                "props": (None, props),
            }
            res = self.REST.rest_post("/resources/{}".format(note_id), files=files)
            return res.json()["id"]
