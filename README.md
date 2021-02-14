OCR Joplin notes
========================

This scrip will try to add OCR data, and possibly a preview image, to notes in Joplin. It will only work on notes with a tag, which must be specified on startup.

### Use cases 
#### 1. As a Joplin user, I want to be able to search for any text, whether it is in the note itself, or in an attachment.
   When making the switch from Evernote to Joplin, there was one thing missing for me.
   Evernote uses OCR on attachments, which makes it possible to do a full text search. This is something that is lacking in Joplin.
   The excellent [rest_uploader](https://github.com/kellerjustin/rest-uploader) has the ability to upload files to Joplin and add OCR data as an HTML comment in the note.
   For existing Joplin notes, either created manually, by the hotfolder plugin or via the Evernote import, the OCR data will not be present.
#### 2. As a Joplin user, I want to have a preview image in the notes I have imported from Evernote.
   Just as notes created by the [rest_uploader](https://github.com/kellerjustin/rest-uploader), I would like to have a nice preview of my PDF documents I've imported from Evernote
                                                                                                                                                                                  
### What this script won't do
* It will not run in the background and automatically update your notes.
  I am considering an option to have a background process check notes with a specific tag to be processed and maybe remove the tag when done.
* It will not update the OCR data once it has been added. Any changes in the note will be ignored.
  Workaround is to manually remove the OCR section from the note and invoke the script again.


**WARNING This script has the potential to mess up all your Joplin notes. But you are not worried, since you make regular backups of your Joplin notes already. Right??**

## Installation
If you already installed [rest_uploader](https://github.com/kellerjustin/rest-uploader) you probably almost setup already.
All that is left is to install this scrip and setup the environment variables.

```shell
pip install ocr-joplin-notes
```

Requirements:
* Joplin's Webclipper must be enabled and your desktop client must be running.
* Required environment variable `JOPLIN_TOKEN`. You can find your token in the webclipper settings.
* Optional environment variable `JOPLIN_SERVER`. If not present it will look for the Joplin client on the current machine
* Environment variable `TESSDATA_PREFIX` On Ubuntu, mine is set to `/usr/share/tesseract-ocr/4.00/tessdata`

### Modes
Since this script will update your notes, several modes have been added, so the user of this script can verify if the detection in this script works as should be expected.

#### Mode: `TAG_NOTES`
Tags all notes in Joplin based on their possible source and markup type.
Apart from adding a tag to every note in Joplin, it does not update any notes.
The tags it adds will not be used by this script itself and can be removed.
It can however be a fast way to tag all your notes. You'll see the need for tags in the other modes.
The format of these tags is: ojn_<markup|html>_<source>.
Example:
* ojn_markup_joplin_desktop
* ojn_html_evernote.mail.smtp
* ojn_html_evernote.mobile.android
* ojn_html_evernote.web.clip

*Parameters*:
* [optional] `--tag`
  When supplied, it will only process notes which have this tag. Default it will process all notes in Joplin.

#### Mode: `DRY_RUN`
Report what will happen if this script would process the notes with a selected tag.
It will report back via the output on the screen, as well as add tags to your notes.
Every note will be tagged with one of the following tags: 
* ojn_ocr_added
* ojn_ocr_failed
* ojn_ocr_skipped

*Parameters*:
* [required] `--tag`="my_tag"
  Only notes having the specified tag will be scanned.
* [optional] `--add-preview`=`on`|`off`
  When `on`, adds a preview image for every PDF found in an HTML note. Default is `on`
  Markdown notes already have a PDF preview in the client.
* [optional] `--autorotation`=`on`|`off`
  When `on` tries to fix any skewed images. Default is `on`
* [optional] `--language`=`<3 letter code>`. 
  The language to use for the OCR processing. Default in `eng`
  
**Note** OCR is quite a CPU intensive process, and it might take some time for large quantities of files to get processed.

#### Mode: `FULL_RUN`
**WARNING: This mode will make changes to your notes. Remember those backups I mentioned before.**

The `FULL_RUN` mode will do the same as the `DRY_RUN` mode, but this time, it **will** make the changes to your Joplin notes.
This is mode you are looking for.

### Command line examples

```shell
ocr-joplin-notes --mode=TAG_NOTES
ocr-joplin-notes --mode=DRY_RUN --tag=my_notes_test --language=nld --add-previews=off
ocr-joplin-notes --mode=FULL_RUN --tag=my_notes_for --language=get 
```


#### Closing remarks
* This is the first Python code I've ever written. It might be crap. It works for me. 
* I don't know if I have the time and energy to keep making updates on this script over time. I might, but it might become abandon-ware someday.
  That's why they've invented forking.
* This is an open source project. You can use it, free of charge.
  Your right to free support and free upgrades does not exist. You might get it, you're not entitled to it.
* It shouldn't happen, but if this script destroys all your data, you still have your those backups, I told you about. Twice.
