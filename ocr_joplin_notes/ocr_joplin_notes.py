import os
from enum import Enum

from .file_ocr import (
    extract_text_from_image,
    extract_text_from_pdf,
    pdf_page_as_image
)
from .joplin_api import (
    find_tag_id,
    create_tag,
    tag_note,
    save_resource_to_file,
    get_note_resources,
    get_resource,
    save_resource,
    perform_on_all_notes,
    perform_on_tagged_notes,
    get_note,
    update_note_body,
)


def set_language(language):
    global LANGUAGE
    LANGUAGE = language


def set_add_previews(add_previews):
    global ADD_PREVIEWS
    ADD_PREVIEWS = True
    if add_previews == "no":
        ADD_PREVIEWS = False


def set_autorotation(autorotation):
    global AUTOROTATION
    AUTOROTATION = True
    if autorotation == "no":
        AUTOROTATION = False


def set_mode(mode):
    global MODE
    MODE = mode


def set_dry_run(safe):
    global DRY_RUN
    DRY_RUN = safe


SCAN_HEADER = "<!--- OCR data inserted below --->"


class ResultTag(Enum):
    OCR_SKIPPED = "ojn_ocr_skipped"
    OCR_FAILED = "ojn_ocr_failed"
    OCR_ADDED = "ojn_ocr_added"


def run_mode(mode, tag):
    if mode == "TAG_NOTES":
        print("Tagging notes. This might take a while. You can follow the progress by watching the tags in Joplin")
        if tag is None:
            perform_on_all_notes(tag_note_with_source)
        else:
            tag_id = find_tag_id(tag)
            if tag_id is None:
                print("tag not found")
                return -1
            perform_on_tagged_notes(tag_note_with_source, tag_id)
        return 0
    elif mode == "DRY_RUN":
        set_dry_run(True)
        return full_run(tag)
    elif mode == "FULL_RUN":
        set_dry_run(False)
        return full_run(tag)
    else:
        print(f"Mode {mode} not supported")
    return -1


def full_run(tag):
    print("Starting OCR for tag {}.".format(tag))
    tag_id = find_tag_id(tag)
    if tag_id is None:
        print("Tag not found or specified")
        return -1
    return perform_on_tagged_notes(perform_ocr_for_note, tag_id)


def tag_note_with_source(note_id):
    note = get_note(note_id)
    if is_note_ocr_ready(note):
        if note.markup_language == 1:
            language = "markup"
        else:
            language = "html"
        tag_title = "ojn_{}_{}".format(language, note.source)
        create_tag(tag_title)
        tag_note(note_id, tag_title)
        return tag_title
    return None


def is_note_ocr_ready(note):
    if is_created_by_rest__uploader(note):
        # Skip notes already containing OCR data
        return False
    elif has_existing_ocr_section(note):
        # Already processed by this script
        return False
    else:
        resources = get_note_resources(note.id)
        for res in resources:
            resource = get_resource(res.get("id"))
            if resource.mime[:5] == "image" or resource.mime == "application/pdf":
                return True
    return False


def has_existing_ocr_section(note):
    return SCAN_HEADER in note.body


def is_created_by_rest__uploader(note):
    """If the note starts with: <filename> uploaded from <host>
    and has a HTML comment section,
    and has at least one attachment
    assume it contains OCR data from the rest_uploader"""
    first_lines = "{}".format(note.body).split("\n", 3)
    file_name = first_lines[0].split(" uploaded from")[0]
    uploaded_from = "uploaded from" in first_lines[0]
    filename_exists = len(file_name) > 0
    comment_start = "\n<!---\n" in note.body
    comment_end = "\n-->\n" in note.body
    markup = note.markup_language == 1
    has_attachment = len(get_note_resources(note.id)) > 0
    return uploaded_from & filename_exists & comment_start & comment_end & markup & has_attachment


def perform_ocr_for_note(note_id):
    note = get_note(note_id)
    result_tag = ocr_resources(note)
    create_tag(result_tag.value)
    tag_note(note_id, result_tag.value)
    return result_tag


def ocr_resources(note):
    print(f"------------------------------------\nnote: {note.title}")
    if is_note_ocr_ready(note):
        result = ""
        resources = get_note_resources(note.id)
        for resource_json in resources:
            resource = get_resource(resource_json.get("id"))
            print(f"- file: {resource.title}")
            data = ocr_resource(resource, ADD_PREVIEWS and note.markup_language == 2)
            if data.pages is not None:
                print(f"  - pages extracted: {len(data.pages)}")
                resulting_text = ""
                if data.input_resource_type == ResourceType.PDF:
                    for i in range(len(data.pages)):
                        resulting_text += "\n---------- [{}/{}] ----------\n{}".format(i + 1, len(data.pages),
                                                                                       data.pages[i])
                else:
                    resulting_text = data.pages[0]
                result += '\n<!-- [{}]\n{}\n-->'.format(resource.title, resulting_text)
                if data.preview_file is not None:
                    title = "preview-{}.png".format(os.path.splitext(os.path.basename(resource.filename))[0])
                    if not DRY_RUN:
                        preview_file_link = add_preview(note, title, data)
                        result += "\n{}\n".format(preview_file_link)
                    os.remove(data.preview_file)
            else:
                print("  - No data found")
        if len(result.strip()) > 0:
            ocr_section = '\n\n{}\n{}\n'.format(SCAN_HEADER, result)
            if not DRY_RUN:
                update_note_body(note.id, note.body + ocr_section)
                print("Result: note updated")
            else:
                print("Result: note would have been updated [dry run]")
            return ResultTag.OCR_ADDED
        else:
            print("Result: note not updated")
            return ResultTag.OCR_FAILED
    else:
        print("Result: skipped")
        return ResultTag.OCR_SKIPPED


def add_preview(note, title, data):
    res_id = save_resource(note.id, data.preview_file, title)
    if note.markup_language == 1:
        preview_file_link = "![{}](:/{})".format(title, res_id)
    else:
        preview_file_link = '<img src=":/{}" alt="{}"/>'.format(res_id, title)
    return preview_file_link


class ResourceType(Enum):
    PDF = "pdf"
    IMAGE = "image"


class OcrResult:
    def __init__(self, pages, input_resource_type=ResourceType.IMAGE, preview_file=None):
        self.pages = pages
        self.input_resource_type = input_resource_type
        self.preview_file = preview_file


def ocr_resource(resource, create_preview=True):
    mime_type = resource.mime
    full_path = save_resource_to_file(resource)
    try:
        if mime_type[:5] == "image":
            result = extract_text_from_image(full_path, auto_rotate=AUTOROTATION, language=LANGUAGE)
            if result is not None:
                return OcrResult(result.pages, ResourceType.IMAGE)
        elif mime_type == "application/pdf":
            ocr_result = extract_text_from_pdf(full_path, language=LANGUAGE)
            if create_preview:
                preview_file = pdf_page_as_image(full_path, is_preview=True)
                return OcrResult(ocr_result.pages, ResourceType.PDF, preview_file)
            else:
                return OcrResult(ocr_result.pages, ResourceType.PDF)
        return OcrResult(None)
    except (TypeError, OSError) as e:
        return OcrResult(None)
    finally:
        os.remove(full_path)
