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

version = 0.702

def application_start(fileName,settings):
	# saved state of the file
	global file_is_saved
	file_is_saved = True

	# takes settings from file or uses default ones
	global style
	if settings is not None:
		style = settings
	else:
		style = "DEFAULT='color=#000 left_margin=2 right_margin=2 font_source=/usr/share/elementary/themes/default.edj font_size=10.000000 font=Sans:style=Regular'em='+ font_style=Oblique'link='+ color=#800 underline=on underline_color=#8008'hilight='+ font_weight=Bold'preedit='+ underline=on underline_color=#000'preedit_sel='+ backing=on backing_color=#000 color=#FFFFFF'"

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
	textbox.callback_changed_user_add(file_saved,window) # allows program to know when file is saved
	textbox.scrollable_set(True) # creates scrollbars rather than enlarge window
	textbox.line_wrap_set(False) # does not allow line wrap (can be changed by user)
	textbox.autosave_set(False) # set to false to reduce disk I/O
	textbox.show()

	# If opened from command line or file manager with the intent of displaying a specific file
	# display this file and change the window title to reflect the current file open.
	if fileName != None:
		textbox.file_set(fileName,elementary.ELM_TEXT_FORMAT_PLAIN_UTF8)
		window.title_set("Etext - "+fileName)

	# what to do when close request is sent
	window.callback_delete_request_add(close_safely,window,textbox)

	# window keybindings
	window.elm_event_callback_add(keybind,window,textbox)

	# create a top menu (toolbar)
	# open button (opens a file)
	open_button = elementary.Button(window)
	open_button.text = "Open"
	open_button.callback_pressed_add(open_pressed,window,textbox)
	open_button.show()

	# new button (clears the editor)
	new_button = elementary.Button(window)
	new_button.text = "New"
	new_button.callback_pressed_add(new_pressed, window, textbox)
	new_button.show()

	# Save As Button (allows saving of new file)
	saveas_button = elementary.Button(window)
	saveas_button.text = "Save As"
	saveas_button.callback_pressed_add(saveas_pressed,window,textbox)
	saveas_button.show()

	# Save Button (save changes to a file)
	save_button = elementary.Button(window)
	save_button.text = "Save"
	save_button.callback_pressed_add(save_pressed,window,textbox)
	save_button.show()

	# Word Wrap toggle (changes the state of word wrap)
	wordwrap_check = elementary.Check(window)
	wordwrap_check.text = "Word Wrap"
	wordwrap_check.callback_changed_add(wordwrap_pressed,window,textbox)
	wordwrap_check.show()

	# Font Button (allows user to change the font size and type)
	font_button = elementary.Button(window)
	font_button.text = "Font"
	font_button.callback_pressed_add(font_pressed,window,textbox)
	font_button.show()

	# About Button (displays about popup)
	about_button = elementary.Button(window)
	about_button.text = "About"
	about_button.callback_pressed_add(about_pressed,window)
	about_button.show()

	# create a horz box to hold buttons
	top_menu = elementary.Box(window)
	top_menu.horizontal_set(True)
	top_menu.size_hint_weight_set(0, 0)
	top_menu.size_hint_align_set(0.01, 0.01)
	top_menu.pack_end(open_button)
	top_menu.pack_end(new_button)
	top_menu.pack_end(save_button)
	top_menu.pack_end(saveas_button)
	top_menu.pack_end(wordwrap_check)
	top_menu.pack_end(font_button)
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

	tmp = textbox.textblock_get().style_set(style)
	window.resize(600,400)

	print textbox.content_get()

def keybind(obj,src_obj,event_type,event,window,textbox):
	global ctrlPressed
	ctrlPressed = False
	global altPressed
	altPressed = False
	if event_type == evas.EVAS_CALLBACK_KEY_DOWN:
		if event.keyname is "Control_L" or "Control_R":
			ctrlPressed = True
		if event.keyname is "Alt_L" or "Alt_R":
			shiftPressed = True
		if ctrlPressed and event.keyname == "s":
			save_pressed(None,window,textbox)
			ctrlPressed == False
		if ctrlPressed and event.keyname == "o":
			open_pressed(None,window,textbox)
			ctrlPressed == False
		if ctrlPressed and event.keyname == "n":
			new_pressed(None,window,textbox)
			ctrlPressed == False
		if ctrlPressed and event.keyname == "q":
			close_safely(None,window,textbox)
			ctrlPressed == False
		if ctrlPressed and altPressed and event.keyname == "s":
			saveas_pressed(None,window,textbox)
			ctrlPressed == False
			altPressed == False

# open_pressed(Button,window,textbox)
# makes sure the current file has been saved. If it has it will proceed
# directly to the file_chooser widget
def open_pressed(open_button,window1,textbox1):
	global file_is_saved
	if not file_is_saved:
		unsaved_popup(window1,textbox1,saveas_pressed)
	else:
		file_chooser(window1,textbox1,False,open_file)

# open_file(Button,file_selected,window,textbox,file_win)
# this takes the output form the file_chooser widget and displays the file
def open_file(Junk,file_selected,window1,textbox1,file_win):
	if file_selected != None:
		textbox1.file_set(file_selected,elementary.ELM_TEXT_FORMAT_PLAIN_UTF8)
		window1.title_set("Etext - "+file_selected)
		file_is_saved = True
	file_win.delete()

# new_pressed(Button,window,textbox)
# looks to see if file is saved. If file is unsaved presents user with options.
# If file is saved will clear the editor
def new_pressed(new_button,window1,textbox1):
	global file_is_saved
	if not file_is_saved:
		unsaved_popup(window1,textbox1,clear_window)
	else:
		clear_window(window1,textbox1)

# clear_window(window1,textbox1)
# will replace the contents of the window with an empty string and reset the window
# title to "Untitled"
def clear_window(window1,textbox1):
	textbox1.entry_set('')
	window1.title_set('Etext - Untitled')

# save_pressed(Button,window,textbox)
# saves the current textbox to file if the file has been specified, if the file has not
# been saved this function will call the saveas_pressed function to save the file.
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
# opens a file_chooser widget in saveas mode. Mainly written as a convenience function.
def saveas_pressed(saveas_button,window1,textbox1):
	file_chooser(window1,textbox1,True,saveas_file)

# saveas_file(Junk,file_selected,window,textbox,file_win)
# this function will go through the steps of saving a new file. It creates a new file
# and then fills it with the contents of the Entry box.
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

# font_pressed(font_button,window,textbox)
# creates a dialog which displays the fonts available on the system and
# allows them to choose the font and size the editor will use.
def font_pressed(font_button,window1,textbox1):
	# inner window to hold GUI for font
	font_win = elementary.InnerWindow(window1)
	font_win.show()

	# Entry to hold sample text
	font_demo = elementary.Entry(font_win)
	font_demo.editable_set(False)
	font_demo.entry_set('Example: the quick brown fox jumped over the lazy dog. 0123456789')
	font_demo.line_wrap_set(False)
	font_demo.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
	font_demo.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
	font_demo.show()

	# spinner to choose the font size
	font_sizer = elementary.Spinner(font_win)
	font_sizer.min_max_set(10,100)
	font_sizer.show()

	# list of System fonts
	fonts_raw = window1.evas.font_available_list()
	fonts = []
	for n in range(len(fonts_raw)):
		tmp = fonts_raw[n].split(":")
		fonts.append(tmp[0])
	# for some strange reason many fonts are displayed multiple times. The following lines remove
	# all duplicates and then sort them alphabetically.
	fonts = list(set(fonts))
	fonts.sort()

	# GenList for holding font options
	font_list = elementary.List(font_win)
	font_list.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
	font_list.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
	for i in range(len(fonts)):
		font_list.item_append(fonts[i], None, None, font_demo_set, fonts[i], font_demo, font_sizer)
	font_list.go()
	font_list.show()

	# Label for Spinner
	font_sizer_label = elementary.Label(font_win)
	font_sizer_label.text = "Font Size:  "
	font_sizer_label.show()

	size_box = elementary.Box(font_win)
	size_box.horizontal_set(True)
	size_box.pack_end(font_sizer_label)
	size_box.pack_end(font_sizer)
	size_box.show()

	# cancel and OK buttons
	ok_button = elementary.Button(font_win)
	ok_button.text = "OK"
	ok_button.callback_pressed_add(font_set, font_list, font_sizer, textbox1, font_win)
	ok_button.show()

	cancel_button = elementary.Button(font_win)
	cancel_button.text = "Cancel"
	cancel_button.callback_pressed_add(close_popup,font_win)
	cancel_button.show()

	# box for buttons
	button_box = elementary.Box(font_win)
	button_box.horizontal_set(True)
	button_box.pack_end(cancel_button)
	button_box.pack_end(ok_button)
	button_box.show()

	# box for Entry (for spacing)
	entry_box = elementary.Box(font_win)
	entry_box.pack_end(font_demo)
	entry_box.size_hint_weight_set(evas.EVAS_HINT_FILL,evas.EVAS_HINT_FILL)
	entry_box.size_hint_weight_set(0.1,0.1)
	entry_box.show()

	# box for everything
	full_box = elementary.Box(font_win)
	full_box.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
	full_box.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
	full_box.pack_end(font_list)
	full_box.pack_end(size_box)
	full_box.pack_end(entry_box)
	full_box.pack_end(button_box)
	full_box.show()

	font_win.content_set(full_box)

# font_demo_set(Junk1, Junk2, Font Selected, Font demo entry, font size spinner)
# This function will change the size and font of the demo text in the font window.
def font_demo_set(Junk, Junk2, font_selected, font_demo, font_size):
	style = "DEFAULT='color=#000 wrap=word left_margin=2 right_margin=2 font_source=/usr/share/elementary/themes/default.edj font_size="+str(font_size.value_get())+"00000 font="+font_selected+":style=Regular'em='+ font_style=Oblique'link='+ color=#800 underline=on underline_color=#8008'hilight='+ font_weight=Bold'preedit='+ underline=on underline_color=#000'preedit_sel='+ backing=on backing_color=#000 color=#FFFFFF'"
	font_demo.textblock_get().style_set(style)

# font_set(ok_button, font_list, font size spinner, textbox1, font window)
# This function will change and the font and size of the text in the editor
def font_set(ok_button, font_list, sizer, textbox1, font_win):
	font_selected = font_list.selected_item_get().text_get()
	font_size = sizer.value_get()
	global style
	style = "DEFAULT='color=#left_margin 000=2 right_margin=2 font_source=/usr/share/elementary/themes/default.edj font_size="+str(font_size)+"00000 font="+font_selected+":style=Regular'em='+ font_style=Oblique'link='+ color=#800 underline=on underline_color=#8008'hilight='+ font_weight=Bold'preedit='+ underline=on underline_color=#000'preedit_sel='+ backing=on backing_color=#000 color=#FFFFFF'"
	textbox1.textblock_get().style_set(style)
	close_popup(None, font_win)

# about_pressed(Button,window1)
# Shows pop-up with very basic information about Etext
def about_pressed(about_button,window1):
	about_popup = elementary.Popup(window1)
	about_popup.size_hint_weight_set(evas.EVAS_HINT_EXPAND,evas.EVAS_HINT_EXPAND)
	about_popup.part_text_set("title,text","Etext v"+str(version))
	about_popup.text = "<b>The Enlightened Text Editor</b><ps>By: Tyler Bradbeer<ps><ps>Etext is licensed under the GNU GPL v2"

	close_button = elementary.Button(window1)
	close_button.text = "OK"
	close_button.callback_clicked_add(close_popup,about_popup)
	about_popup.part_content_set("button1",close_button)

	about_popup.show()

# Simple function for changing the save state of the file
def file_saved(textbox,window1):
	global file_is_saved
	file_is_saved = False
	temp = window1.title_get()
	if not temp[0] == '*':
		window1.title_set('*'+temp)
	global style
	textbox.textblock_get().style_set(style)

# close_popup(button,popup)
# simple function to close any popup
def close_popup(button,popup1):
	popup1.delete()

# close_safely(junk,window,textbox)
# function looks to make sure file has been saved and offers options to the user
# if the current file has not been saved.
def close_safely(Junk,window1,textbox1):
	if file_is_saved:
		close_nolook(None,window1,textbox1)
	else:
		unsaved_popup(window1,textbox1,close_nolook)

# file_choser(window,textbox,save_mode <bool>,function)
# I wrote this because the FileselectorButton does not allow control of when the file selector
# pops up. This allows me to place a popup before the file selection process begins.
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
# produces a pop-up which provides options on what to do because the file has not been saved
def unsaved_popup(window1,textbox1,function1):
	# Create popup
	unsaved_popup = elementary.Popup(window1)
	unsaved_popup.part_text_set("title,text","File Unsaved!")
	unsaved_popup.text = "The current file has not been saved.<ps>what would you like to do?"
	# Close without saving button
	clc_no_save_btt = elementary.Button(window1)
	clc_no_save_btt.text = "Close Without Saving"
	clc_no_save_btt.callback_clicked_add(function1,window1,textbox1)
	clc_no_save_btt.show()
	# Save the file and then close button
	clc_save_btt = elementary.FileselectorButton(window1)
	clc_save_btt.expandable_set(False)
	clc_save_btt.inwin_mode_set(True)
	clc_save_btt.is_save_set(True)
	if textbox1.file_get()[0] != None:
		clc_save_btt.path_set(textbox1.file_get()[0])
	clc_save_btt.callback_file_chosen_add(saveas_file,None,window1,textbox1)
	clc_save_btt.text = "Save File"
	clc_save_btt.show()
	# cancel close request
	cancel_btt = elementary.Button(window1)
	cancel_btt.text = "Cancel"
	cancel_btt.callback_clicked_add(close_popup,unsaved_popup)
	cancel_btt.show()
	# add buttons to popup
	unsaved_popup.part_content_set("button1",clc_no_save_btt)
	unsaved_popup.part_content_set("button2",clc_save_btt)
	unsaved_popup.part_content_set("button3",cancel_btt)
	unsaved_popup.show()

# close_nolook(self,textbox)
# function will close the current window no matter what. This function will also write some settings
# to a file so that they can be used next time. These settings are the location of the editor on the
# screen, the size of the editor window and the font size and style.
def close_nolook(Junk,window1,textbox1):
	if not os.path.exists(os.path.expanduser('~')+"/.e/e/applications/Etext/settings"):
		os.makedirs(os.path.expanduser('~')+"/.e/e/applications/Etext/")
	else:
		os.remove(os.path.expanduser('~')+"/.e/e/applications/Etext/settings")
	f = open(os.path.expanduser('~')+"/.e/e/applications/Etext/settings",'w')
	global style
	f.write(style)
	elementary.exit()

# This function reads the user settings from the settings file and puts them in a list.
def read_settings():
	f = open(os.path.expanduser('~')+"/.e/e/applications/Etext/settings",'r')
	global style
	style = f.readline().strip()
	return style

# this is the main command that runs the entire program
if __name__ == "__main__":
	# The first conditional determines if the file was opened in the program from the command line
	# The second conditional determines if a settings file exists.
	isFile = len(sys.argv) == 2
	isSettings = os.path.exists(os.path.expanduser('~')+"/.e/e/applications/Etext/settings")

	# This little clusterf@#! of if statements deals with all of the possibilities involving
	# settings and files opened
	if isFile and isSettings:
		settings = read_settings()
		application_start(sys.argv[1],settings)
	elif isFile and not isSettings:
		application_start(sys.argv[1],None)
	elif not isFile and isSettings:
		settings = read_settings()
		application_start(None,settings)
	else: # not isFile and not isSettings
		application_start(None,None)

	elementary.run()
	elementary.shutdown()