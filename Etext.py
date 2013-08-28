#!/usr/bin/env python
#
# Etext: the enlightened text editor
# Written by Tyler Bradbeer
# Etext is licensed under the GNU GPLv2

# Imports
import elementary
import evas
import sys
import os

version = 0.10

def application_start(fileName):
	# Create the window title and boarder
	window = elementary.StandardWindow("Etext", "Etext - Untitled")
	window.show()

	# Add window Icon
	icon = elementary.Image(window)
	icon.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
	icon.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
	icon.file_set('Etext.png') # assumes image icon is in local dir, may need to change later
	icon.show()
	window.icon_object_set(icon.object_get())

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
	file_is_saved = True

	# create a top menu (toolbar)
	# open button
	open_button = elementary.Button(window)
	open_button.text = "Open"
	open_button.callback_pressed_add(open_pressed,window,textbox)
	open_button.show()

	# clears the editor
	new_button = elementary.Button(window)
	new_button.text = "New"
	new_button.callback_pressed_add(new_pressed, window, textbox)
	new_button.show()

	# Save As Button 
	saveas_button = elementary.Button(window)
	saveas_button.text = "Save As"
	saveas_button.callback_pressed_add(saveas_pressed,window,textbox)
	saveas_button.show()

	# Save Button
	save_button = elementary.Button(window)
	save_button.text = "Save"
	save_button.callback_pressed_add(save_pressed,window,textbox)
	save_button.show()

	# Word Wrap toggle
	wordwrap_check = elementary.Check(window)
	wordwrap_check.text = "Word Wrap"
	wordwrap_check.callback_changed_add(wordwrap_pressed,window,textbox)
	wordwrap_check.show()

	# About Button
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
	full_package.padding_set(1,1)
	full_package.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
	full_package.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)

	full_package.pack_end(top_menu)
	full_package.pack_end(textbox)

	full_package.show()

	window.resize_object_add(full_package)
	window.resize(600,400)

# open_pressed(Button,window,textbox)
# makes sure the current file has been saved. If it has it will proceed
# directly to the file_chooser widget
def open_pressed(open_button,window1,textbox1):
	global file_is_saved
	if not file_is_saved:
		unsaved_popup(window1,textbox1,saveas_pressed)
	else:
		file_chooser(window1,textbox1,False,open_file)

# open_file(Crap,file_selected,window,textbox,file_win)
# this takes the output form the file_chooser widget and displays the file 
def open_file(Junk,file_selected,window1,textbox1,file_win):
	if file_selected != None:
		textbox1.file_set(file_selected,elementary.ELM_TEXT_FORMAT_PLAIN_UTF8)
		window1.title_set("Etext - "+file_selected)
		file_is_saved = True
	file_win.delete()

# new_pressed(Button,window,textbox)
# clears the current file and starts a new blank one
def new_pressed(new_button,window1,textbox1):
	global file_is_saved
	if not file_is_saved:
		unsaved_popup(window1,textbox1,saveas_pressed)
	else:
		textbox1.clear()

# save_pressed(Button,window,textbox)
# saves the current textbox to file if the file has been specified if not warns
# user and instructs them to use the saveas button
def save_pressed(save_button,window1,textbox1):
	temp = textbox1.file_get();
	if temp == (None,0):
		saveas_pressed(None,window1,textbox1)
	else:
		textbox1.file_save()
		window1.title_set("Etext - "+temp[0])
		global file_is_saved
		file_is_saved = True

# saveas_pressed(saveas_button,window,textbox)
# this function is only used because I have to call it in 2 places
def saveas_pressed(saveas_button,window1,textbox1):
	file_chooser(window1,textbox1,True,saveas_file)

# saveas_file(Junk,file_selected,window,textbox,file_win)
# this function will go through the steps of saving the file 		
def saveas_file(Junk,file_selected,window1,textbox1,file_win):
	if file_selected != None:
		open(file_selected,'w').close() # creates new file
		tmp_text = textbox1.entry_get()
		textbox1.file_set(file_selected,elementary.ELM_TEXT_FORMAT_PLAIN_UTF8)
		textbox1.entry_set(tmp_text)
		textbox1.file_save()
		global file_is_saved
		file_is_saved = True
		window1.title_set("Etext - "+file_selected)
	file_win.delete()

# wordwrap_pressed(Check,window,textbox)
# function toggles the state of wordwrap in the textbox
def wordwrap_pressed(wordwrap_check,window1,textbox1):
	temp = wordwrap_check.state_get()
	if temp:
		textbox1.line_wrap_set(True)
	else:
		textbox1.line_wrap_set(False)

# about_pressed(Button,window1)
# Shows pop-up with very basic information
def about_pressed(about_button,window1):
	about_popup = elementary.Popup(window1)
	about_popup.part_text_set("title,text","Etext v"+str(version))
	about_popup.part_text_set("default","<b>The Enlightened Text Editor</b><ps>\
										By: Tyler Bradbeer<ps><ps>\
										Etext is licensed under the GNU GPL v2")
	close_button = elementary.Button(window1)
	close_button.text = "OK"
	close_button.callback_clicked_add(close_popup,about_popup)
	about_popup.part_content_set("button1",close_button)
	about_popup.show()
	
# Simple function for changing the save state of the file
def file_saved(Junk,window1):
	global file_is_saved
	file_is_saved = False
	temp = window1.title_get()
	if not temp[0] == '*':
		window1.title_set('*'+temp)

# close_popup(button,popup)
# simple function to close any popup
def close_popup(button,popup1):
	popup1.delete()

# close_safely(junk,window,textbox)
# function looks to make sure file has been saved and offers options to the user
# if the current file has not been saved.
def close_safely(Junk,window1,textbox1):
	if file_is_saved:
		close_nolook(None,window1)
	else:
		unsaved_popup(window1,textbox1,close_nolook)

# file_choser(window,textbox,save_mode <bool>,function)
# I wrote this because the FileselectorButton does not have enough options
# it offers the same basic functions but has more options available 
def file_chooser(window1,textbox1,save_mode,function):
	file_win = elementary.InnerWindow(window1)
	file_stuff = elementary.Fileselector(file_win)
	file_stuff.expandable_set(False)
	file_stuff.is_save_set(save_mode)
	file_stuff.buttons_ok_cancel_set(True)
	file_stuff.callback_done_add(function,window1,textbox1,file_win)
	file_stuff.path_set(os.getcwd())
	file_stuff.show()
	file_win.content_set(file_stuff)
	file_win.show()

# unsaved_popup(window,textbox,function)
#produces a pop-up which provides options on what to do because the file has not been saved 
def unsaved_popup(window1,textbox1,function1):
	# Create popup
	unsaved_popup = elementary.Popup(window1)
	unsaved_popup.part_text_set("title,text","File Unsaved!")
	unsaved_popup.part_text_set("default","The current file has not been saved.<ps> what would you like to do?")
	# Close without saving button
	clc_no_save_btt = elementary.Button(window1)
	clc_no_save_btt.text = "Close Without Saving"
	clc_no_save_btt.callback_clicked_add(function1,window1)
	# Save the file and then close button
	clc_save_btt = elementary.FileselectorButton(window1)
	clc_save_btt.expandable_set(False)
	clc_save_btt.inwin_mode_set(True)
	clc_save_btt.is_save_set(True)
	if textbox1.file_get()[0] != None:
		clc_save_btt.path_set(textbox1.file_get()[0])
	clc_save_btt.callback_file_chosen_add(saveas_file,None,window1,textbox1)
	clc_save_btt.text = "Save File"
	# cancel close request
	cancel_btt = elementary.Button(window1)
	cancel_btt.text = "Cancel"
	cancel_btt.callback_clicked_add(close_popup,unsaved_popup)
	# add buttons to popup
	unsaved_popup.part_content_set("button1",clc_no_save_btt)
	unsaved_popup.part_content_set("button2",clc_save_btt)
	unsaved_popup.part_content_set("button3",cancel_btt)
	unsaved_popup.show()

# close_nolook(self,window)
# function will close the current window no matter what
# BUG: This closes all elementary applications rather than the only the one window
def close_nolook(Junk,window1):
	#window1.delete()
	elementary.exit()

if __name__ == "__main__":
	if len(sys.argv) == 1:
		application_start(None)
	else:
		application_start(sys.argv[1])

	elementary.run()
	elementary.shutdown()