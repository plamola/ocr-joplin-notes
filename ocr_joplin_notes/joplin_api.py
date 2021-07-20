import json
import tempfile

from .rest import (
    rest_get,
    rest_put,
    rest_post,
    rest_post_file,
    rest_delete,
)


class JoplinNote:
    def __init__(self, json_data):
        self.id = json_data.get("id")
        self.title = json_data.get("title")
        self.body = json_data.get("body")
        self.source = json_data.get("source")
        self.markup_language = json_data.get("markup_language")


class JoplinResource:
    def __init__(self, json_data):
        self.id = json_data.get("id")
        self.filename = json_data.get("filename")
        self.mime = json_data.get("mime")
        self.title = json_data.get("title")


def paginate_by_title(page: int):
    return 'order_by=title&limit=10&page={}'.format(page)
    

def get_all_tags(note_id: str):
    if note_id is None:
        return None
    res = rest_get('/notes/{}/tags?fields=title'.format(note_id))
    tags = res.json()["items"]
    list_of_tags = list([dic.get("title") for dic in tags])
    return list_of_tags


def find_tag_id(title: str, page: int = 1):
    if title is None:
        return None
    res = rest_get('/tags?{}'.format(paginate_by_title(page)))
    tags = res.json()["items"]
    for tag in tags:
        if tag.get("title") == title:
            return tag.get("id")
    if res.json()["has_more"]:
        return find_tag_id(title, page + 1)
    else:
        return None


def create_tag(title):
    tag_id = find_tag_id(title.lower())
    if tag_id is None:
        res = rest_post("/tags", '{{ "title" : {} }}'.format(json.dumps(title)))
        tag_id = res.json()["id"]
    return tag_id


def delete_tag(title):
    tag_id = find_tag_id(title)
    if tag_id is not None:
        res = rest_delete("/tags/{}".format(tag_id))
        return res.status_code
    return None


def tag_note(note_id, tag_title):
    tag_id = find_tag_id(tag_title)
    res = rest_post("/tags/{}/notes".format(tag_id), '{{ "id" : {} }}'.format(json.dumps(note_id)))
    return tag_id


def perform_on_tagged_notes(usage_function, tag_id, exclude_tags, page: int = 1):
    res = rest_get('/tags/{}/notes?{}'.format(tag_id, paginate_by_title(page)))
    notes = res.json()["items"]
    for note in notes:
        note_id = note.get("id")
        all_tags = get_all_tags(note_id)     # get all tags of the current note
        # check if any tag in the list exclude_tags is equal to any tag of the current notes' tags
        if len(set(exclude_tags).intersection(all_tags)) == 0:  
            # print(note.get("title"), end=" : ")
            usage_function(note_id)
        else:
            note = get_note(note_id)
            print(f"------------------------------------\nnote: {note.title}")
            print("Excluding this note\n")
    if res.json()["has_more"]:
        return perform_on_tagged_notes(usage_function, tag_id, exclude_tags, page + 1)
    else:
        return 0


def perform_on_all_notes(usage_function, page: int = 1):
    res = rest_get('/notes?{}'.format(paginate_by_title(page)))
    notes = res.json()["items"]
    for note in notes:
        # print(note.get("title"), end=" : ")
        usage_function(note.get("id"))
    if res.json()["has_more"]:
        return perform_on_all_notes(usage_function, page + 1)
    else:
        return None


def get_note(note_id):
    res = rest_get('/notes/{}?fields=id,title,body,source,markup_language'.format(note_id))
    return JoplinNote(res.json())


def update_note_body(note_id, new_body: str):
    res = rest_put("/notes/{}".format(note_id), '{{ "body" : {} }}'.format(json.dumps(new_body)))


def save_resource_to_file(resource: JoplinResource):
    file_download = rest_get('/resources/{}/file?dummy=dummy'.format(resource.id))
    full_path = tempfile.mktemp(dir=tempfile.tempdir)
    open(full_path, 'wb').write(file_download.content)
    return full_path


def get_note_resources(note_id):
    res = rest_get("/notes/{}/resources/?dummy=dummy".format(note_id))
    return res.json()["items"]


def get_resource(resource_id):
    res = rest_get("/resources/{}?fields=id,title,filename,mime".format(resource_id))
    return JoplinResource(res.json())


def save_resource(note_id, filename: str, title: str):
    res = rest_post_file("/resources/{}".format(note_id), filename, f'{{"title":"{title}", "filename":"{title}.png"}}')
    return res.json()["id"]
