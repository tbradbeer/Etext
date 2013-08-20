#!/usr/bin/env python
# Etext: the enlightend text editor
# Written by Tyler Bradbeer
# Etext is licensed under the GNU GPLv2

# Imports
import elementary
import evas
import sys

def application_start(fileName):
	# Create the window title and boarder
	window = elementary.StandardWindow("Etext", "Etext - Untitled")
	window.show()

	# creates textbox to hold text
	textbox = elementary.Entry(window)
	textbox.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
	textbox.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
	textbox.callback_changed_user_add(file_saved,window)
	textbox.scrollable_set(True) # creates scrollbars rather than enlarge window
	textbox.line_wrap_set(False) # does not allow line wrap
	textbox.autosave_set(False) # set to false to reduce disk IO
	textbox.show()

	if fileName != None:
		textbox.file_set(fileName,elementary.ELM_TEXT_FORMAT_PLAIN_UTF8)

	# what to do when close request is sent
	window.callback_delete_request_add(close_safely,window,textbox)

	# saved state of the file
	global file_is_saved
	file_is_saved = False

	# create a top menu (toolbar)
	# open button
	open_button = elementary.FileselectorButton(window)
	open_button.text = "Open"
	open_button.window_title_set("Open...")
	open_button.expandable_set(False)
	open_button.inwin_mode_set(True)
	open_button.callback_file_chosen_add(open_pressed, window, textbox)
	open_button.show()

	# clears the editor
	new_button = elementary.Button(window)
	new_button.text = "New"
	new_button.callback_pressed_add(new_pressed, window, textbox)
	new_button.show()

	saveas_button = elementary.FileselectorButton(window)
	saveas_button.text = "Save As"
	saveas_button.callback_file_chosen_add(saveas_pressed,window,textbox)
	saveas_button.window_title_set("Save As...")
	saveas_button.expandable_set(False)
	saveas_button.inwin_mode_set(True)
	saveas_button.is_save_set(True)
	saveas_button.show()

	save_button = elementary.Button(window)
	save_button.text = "Save"
	save_button.callback_pressed_add(save_pressed,window,textbox)
	save_button.show()

	wordwrap_check = elementary.Check(window)
	wordwrap_check.text = "Word Wrap"
	wordwrap_check.callback_changed_add(wordwrap_pressed,window,textbox)
	wordwrap_check.show()

	about_button = elementary.Button(window)
	about_button.text = "About"
	about_button.callback_pressed_add(about_pressed,window)
	about_button.show()

	# create a horz box to hold buttons
	top_menu = elementary.Box(window)
	top_menu.horizontal_set(True)
	top_menu.size_hint_weight_set(0, 0)
	top_menu.size_hint_align_set(0, 0)
	top_menu.pack_end(open_button)
	top_menu.pack_end(new_button)
	top_menu.pack_end(save_button)
	top_menu.pack_end(saveas_button)
	top_menu.pack_end(wordwrap_check)
	top_menu.pack_end(about_button)

	top_menu.show()

	# Create a box to hold everything
	full_package = elementary.Box(window)
	full_package.padding_set(2,2)
	full_package.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
	full_package.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)

	full_package.pack_end(top_menu)
	full_package.pack_end(textbox)

	full_package.show()

	window.resize_object_add(full_package)
	window.resize(500,300)


# open_pressed(FileselectorButton,file_selected,window,textbox)
# function will replace the contents of the textbox with those from
# the chosen file. It should make sure that the current file has been saved.
def open_pressed(open_button,file_selected,window1,textbox1):
	# Look to make sure the current file has been saved
	textbox1.file_set(file_selected,elementary.ELM_TEXT_FORMAT_PLAIN_UTF8)
	window1.title_set("Etext - "+file_selected)
	file_is_saved = True

# new_pressed(Button,window,textbox)
# starts a new instance of Etext
def new_pressed(new_button,argument1,argument2):
	application_start(None)

# save_pressed(Button,window,textbox)
# saves the current textbox to file if the file has been specified if not warns
# user and instructs them to use the saveas button
def save_pressed(save_button,window1,textbox1):
	temp = textbox1.file_get();
	# This ensures that the file is saved using the saveas function first
	# This is not ideal and should be replaced with a function that calls save_as correctly
	if temp == (None,0):
		saveas_popup = elementary.Popup(window1)
		saveas_popup.part_text_set("title,text","File Has No Name")
		saveas_popup.part_text_set("default","File has never been saved please use Save As")
		saveas_popup_button = elementary.Button(window1)
		saveas_popup_button.text = "OK"
		saveas_popup_button.callback_clicked_add(close_popup,saveas_popup)
		saveas_popup.part_content_set("button1",saveas_popup_button)
		saveas_popup.show()
	else:
		argument2.file_save()
		file_is_saved = True

# saveas_pressed(FileselectorButton,file_selected,textbox)
# function creates a new file with the name and place specified by the user
# and then writes the contents of the textbox to this file
def saveas_pressed(saveas_button,file_selected,window1,textbox1):
	if file_selected != None:
		tmp_file = open(file_selected,'w').close() # creates new file
		tmp_text = textbox1.entry_get()
		textbox1.file_set(file_selected,elementary.ELM_TEXT_FORMAT_PLAIN_UTF8)
		textbox1.entry_set(tmp_text)
		textbox1.file_save()
		file_is_saved = True
		window1.title_set("Etext - "+file_selected)

# wordwrap_pressed(Check,window,textbox)
# function toggles the state of wordwrap in the textbox
def wordwrap_pressed(wordwrap_check,window1,textbox1):
	temp = wordwrap_check.state_get()
	if temp:
		textbox1.line_wrap_set(True)
	else:
		textbox1.line_wrap_set(False)

# about_pressed(Button,window1)
# Shows popup with very basic information
def about_pressed(about_button,window1):
	about_popup = elementary.Popup(window1)
	about_popup.part_text_set("title,text","Etext v0.01")
	about_popup.part_text_set("default","<b>The Enlightened Text Editor</b><ps>\
										By: Tyler Bradbeer<ps><ps>\
										Etext is licensed under the GNU GPL v2")
	close_button = elementary.Button(window1)
	close_button.text = "OK"
	close_button.callback_clicked_add(close_popup,about_popup)
	about_popup.part_content_set("button1",close_button)
	about_popup.show()

def file_saved(self,window1):
	file_is_saved = False
	print "You are here"

# close_popup(button,popup)
# simple function to close any popup
def close_popup(button,popup1):
	popup1.delete()

# close_safely(self,window,textbox)
# function looks to make sure file has been saved and offers options to the user
# if the current file has not been saved.
def close_safely(self,window1,textbox1):
	if file_is_saved:
		close_nolook(window1)
	else:
		# Create popup
		unsaved_popup = elementary.Popup(self)
		unsaved_popup.part_text_set("title,text","File Unsaved!")
		unsaved_popup.part_text_set("default","This file has not been saved what would you like to do?")
		# Close without saving button
		clc_no_save_btt = elementary.Button(self)
		clc_no_save_btt.text = "Close Without Saving"
		clc_no_save_btt.callback_clicked_add(close_nolook,window1)
		# Save the file and then close button
		clc_save_btt = elementary.FileselectorButton(self)
		clc_save_btt.expandable_set(False)
		clc_save_btt.inwin_mode_set(True)
		clc_save_btt.is_save_set(True)
		if textbox1.file_get()[0] != None:
			clc_save_btt.path_set(textbox1.file_get()[0])
		#clc_save_btt.callback_file_chosen_add()
		clc_save_btt.text = "Save File"
		# cancel close request
		cancel_btt = elementary.Button(self)
		cancel_btt.text = "Cancel"
		cancel_btt.callback_clicked_add(close_popup,unsaved_popup)
		# add buttons to popup
		unsaved_popup.part_content_set("button1",clc_no_save_btt)
		unsaved_popup.part_content_set("button2",clc_save_btt)
		unsaved_popup.part_content_set("button3",cancel_btt)
		unsaved_popup.show()

# close_nolook(self,window)
# function will close the current window no matter what
# BUG: This deletes the current window and leaves all other instances of Etext alone
#		however after all Etext windows are closed the program continues to run.
def close_nolook(self,window1):
	#window1.delete()
	elementary.exit()


if __name__ == "__main__":
	if len(sys.argv) == 1:
		application_start(None)
	else:
		application_start(sys.argv[1])

    #Starts an elementary event loop which displays all elementary objects we've created.
    # Our code stays at this point until elementary.exit() is called
	elementary.run()

    #Once elementary is done running lets shut everything off to finish the application
	elementary.shutdown()