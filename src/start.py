"""Start the GACP GUI"""
import os
import csv

import wx

import cookie_parser



# Template for the domain info panel. We use format to substitute the parsed
# domain cookie values in, meaning that the {format names} are actually the
# keys of the return value of cookie_parser.ga_parse
DOMAIN_INFO_TEMPLATE = """Domain Info: (source)
First visit: {time_first_visit} (_ga)
Most recent visit: {time_most_recent_visit} (__utma)
Second most recent visit: {time_2nd_most_recent_visit} (__utma)
Number of visits: {count_visits_utma} (__utma)
Number of visits: {count_visits_utmz} (__utmz)

Current session start: {time_session_start} (__utma)
Pageviews in this session: {count_session_pageviews} (__utmb)

Search term used: {value_search_term} (__utmz)
Source of visit: {value_visit_source} (__utmz)

Number of outbound clicks: {count_outbound_clicks} (__utmb)

Client identifier: {value_client_identifier} (_ga)
Visitor identifier: {value_visitor_identifier} (__utma)"""

# Stores the file filters of each browser and version, used when selecting a file
BROWSER_FILETYPES = {
    "firefox.3+": "SQLite3 files (*.sqlite)|*.sqlite"
}

# The instructions for each browser and version
BROWSER_INSTRUCTIONS = {
    "firefox.3+": "Locate the cookies.sqlite file, typically found in \
%localappdata%\\Mozilla\\Firefox\\Profiles\\<random text>.default \
or %appdata%\\Mozilla\\Firefox\\Profiles\\<random text>.default"""
}

# Convert the names in the browser selection dropdown to 'short names', which
# are independent of how the browser name and version are displayed
BROWSER_SHORTNAMES = {
    "Firefox v3+": "firefox.3+"
}

# WX styles for a display textarea
TEXTCTRL_DISPLAY_STYLES = wx.ALIGN_LEFT | wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_BESTWRAP

# The width of the column of setting labels
LABEL_COLUMN_WIDTH = 150

class MainWindow(wx.Frame):
    """
    Main application window Frame
    """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(500, 400))

        self.parser = None

        self.SetIcon(wx.Icon("icon.png"))

        self.SetMinSize(wx.Size(420, 420))
        self.SetMaxSize(wx.Size(700, 100000))

        outer_sizer = wx.BoxSizer(wx.VERTICAL)

# ---------- START OF SETTINGS PANE ---------- #

        # Settings pane, with labels on left and controls on right
        self.settings_frame = wx.Panel(self)
        settings_sizer = wx.GridBagSizer(vgap=0, hgap=0)

        # Sizer flags and args, with standard spacing to avoid repeating
        # them everywhere
        setting_sizer_args = dict(flag=wx.EXPAND | wx.ALL, border=10)

        # Browser selection
        label_browser_choice = wx.StaticText(self.settings_frame,
                                             label="Browser and Version",
                                             style=wx.ALIGN_LEFT)

        # Use this to force a width of the label column
        label_browser_choice.SetMinSize((LABEL_COLUMN_WIDTH, 0))

        settings_sizer.Add(label_browser_choice, wx.GBPosition(0, 0), **setting_sizer_args)

        # Browser/version dropdown
        self.setting_browser_choice = wx.Choice(self.settings_frame, choices=["Firefox v3+"])
        self.setting_browser_choice.SetSelection(0)
        settings_sizer.Add(self.setting_browser_choice, wx.GBPosition(0, 1), **setting_sizer_args)

        # Browser-specific instructions
        self.browser_instructions = wx.TextCtrl(self.settings_frame,
                                                value="",
                                                style=TEXTCTRL_DISPLAY_STYLES,
                                                size=(-1, 100))
        settings_sizer.Add(self.browser_instructions,
                           wx.GBPosition(1, 0),
                           wx.GBSpan(1, 2),
                           **setting_sizer_args)

        settings_sizer.AddGrowableRow(1)
        # File selection
        label_file_input = wx.StaticText(self.settings_frame,
                                         label="Input File",
                                         style=wx.ALIGN_LEFT)
        settings_sizer.Add(label_file_input, wx.GBPosition(2, 0), **setting_sizer_args)

        setting_file_input_container = wx.Panel(self.settings_frame)
        setting_file_input_container_sizer = wx.GridBagSizer(vgap=0, hgap=10)

        self.setting_file_input = wx.TextCtrl(setting_file_input_container, value="")
        self.setting_file_input_browse = wx.Button(setting_file_input_container, label="Browse")

        self.setting_file_input_browse.Bind(wx.EVT_BUTTON, self.on_browse_path)

        # Browse path and button together
        setting_file_input_container_sizer.Add(self.setting_file_input,
                                               wx.GBPosition(0, 0),
                                               flag=wx.EXPAND | wx.HORIZONTAL)

        setting_file_input_container_sizer.Add(self.setting_file_input_browse,
                                               wx.GBPosition(0, 1))

        # Allow the input textbox to expand
        setting_file_input_container_sizer.AddGrowableCol(0)

        setting_file_input_container.SetSizer(setting_file_input_container_sizer)

        settings_sizer.Add(setting_file_input_container, wx.GBPosition(2, 1), **setting_sizer_args)

        # Submit button

        self.setting_process = wx.Button(self.settings_frame, label="Process")
        settings_sizer.Add(self.setting_process,
                           wx.GBPosition(3, 0),
                           wx.GBSpan(1, 2),
                           **setting_sizer_args)
        self.setting_process.Bind(wx.EVT_BUTTON, self.on_process)

        settings_sizer.AddGrowableCol(1)
        self.settings_frame.SetSizer(settings_sizer)

        outer_sizer.Add(self.settings_frame, wx.SizerFlags().Expand())

# ---------- END OF SETTINGS PANE ---------- #

        separator = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        outer_sizer.Add(separator, wx.SizerFlags().Expand())

# ---------- START OF OUTPUT PANE ---------- #

        # Output viewing
        self.output_frame = wx.Panel(self)
        output_sizer = wx.GridBagSizer(vgap=0, hgap=0)

        # Convert to .csv button
        self.setting_csv_button = wx.Button(self.output_frame, label="Output to .csv")
        output_sizer.Add(self.setting_csv_button,
                         wx.GBPosition(0, 0),
                         wx.GBSpan(1, 2),
                         **setting_sizer_args)
        self.setting_csv_button.Bind(wx.EVT_BUTTON, self.on_export_csv)

        # Label for the domain to view
        label_view_domain = wx.StaticText(self.output_frame, label="Domain", style=wx.ALIGN_LEFT)
        # Forces the width of the label column
        label_view_domain.SetMinSize((LABEL_COLUMN_WIDTH, 0))

        output_sizer.Add(label_view_domain, wx.GBPosition(1, 0), **setting_sizer_args)

        # Combobox for the setting for the domain to view
        self.setting_view_domain = wx.ComboBox(self.output_frame, choices=[])

        self.setting_view_domain.Bind(wx.EVT_COMBOBOX, self.on_select_domain)

        output_sizer.Add(self.setting_view_domain, wx.GBPosition(1, 1), **setting_sizer_args)

        # Textbox which displays the output of the domain info
        self.domain_info = wx.TextCtrl(self.output_frame,
                                       value="",
                                       style=TEXTCTRL_DISPLAY_STYLES,
                                       size=(-1, 200))
        output_sizer.Add(self.domain_info,
                         wx.GBPosition(2, 0),
                         wx.GBSpan(1, 2),
                         **setting_sizer_args)

        self.output_frame.SetSizer(output_sizer)
        outer_sizer.Add(self.output_frame, 1, wx.EXPAND|wx.ALL)

        # Hints to user that output controls cannot be used until file is opened
        self.output_frame.Enable(False)

        output_sizer.AddGrowableCol(1)

# ---------- END OF OUTPUT PANE ---------- #

        self.SetSizer(outer_sizer)

        self.status_bar = self.CreateStatusBar() # A StatusBar in the bottom of the window

        self.status_bar.SetStatusText('Ready')

        # Setting up the menu.
        filemenu = wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard ids provided by wxWidgets.
        menu_about = filemenu.Append(wx.ID_ABOUT, "&About", " Information about this program")
        menu_exit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")

        # Creating the menu_bar.
        menu_bar = wx.MenuBar()
        menu_bar.Append(filemenu, "&File")
        self.SetMenuBar(menu_bar)

        # Set events.
        self.Bind(wx.EVT_MENU, self.on_about, menu_about)
        self.Bind(wx.EVT_MENU, self.on_exit, menu_exit)

        self.Show(True)

        # Initialise the browser instruction text to the current selection
        self.update_browser()

    def show_message(self, title, message, message_type=wx.ICON_ERROR):
        """
        Show a dialog information or warning with the specified type
        """
        popup = wx.MessageDialog(self, message, title, wx.OK | message_type)
        popup.ShowModal()
        popup.Destroy()

    def get_browser_name(self):
        """
        Returns the currently selected browser's short name
        """

        selection_index = self.setting_browser_choice.GetSelection()

        selection_name = self.setting_browser_choice.GetString(selection_index)

        return BROWSER_SHORTNAMES[selection_name]

    def update_browser(self):
        """
        Updates the browser instruction text based on the selected browser
        """
        browser_text = BROWSER_INSTRUCTIONS[self.get_browser_name()]

        # Add a zero width space so that the instructions are wrapped at \
        self.browser_instructions.SetValue(browser_text.replace("\\", "\\\u200b"))

    def update_domain_info(self):
        """
        Updates the domain information with the selected domain
        """
        class Default(dict):
            """
            Class inheriting from dict, whose purpose is to provide
            the <not-found> string rather than raising when a key
            is not found
            """
            def __missing__(self, key):
                return '<not found>'

        domain = self.setting_view_domain.GetValue()

        # Create our dict with the format placeholder names as keys
        info_dict = Default(self.parser.get_domain_info(domain))

        self.domain_info.SetValue(DOMAIN_INFO_TEMPLATE.format_map(info_dict))

    def on_select_domain(self, event):
        """
        When a new domain is selected from the dropdown we should fetch
        its cookie info and update the domain info display
        """
        self.update_domain_info()
        event.Skip()

    def on_export_csv(self, _):
        """
        When Export to CSV is clicked
        """
        with wx.DirDialog(self,
                          "Set .csv output folder",
                          style=wx.DD_DEFAULT_STYLE) as folder_dialog:

            if folder_dialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            pathname = folder_dialog.GetPath()

        filenames = {"_ga": "cookie_ga.csv",
                     "__utma": "cookie__utma.csv",
                     "__utmb": "cookie__utmb.csv",
                     "__utmz": "cookie__utmz.csv"}

        conflicts = [] # Planned export filenames which already exist in the target folder

        for filename in filenames.values():
            # If we find a conflict...
            if os.path.exists(os.path.join(pathname, filename)):
                conflicts.append(filename) # Add it to the list

        if conflicts: # If there was a conflict
            # Prepare a dialog window
            message = "{} already exist(s).\n"\
                      "Do you want to replace it/them?".format(", ".join(conflicts))

            popup = wx.MessageDialog(self, message, "Confirm export", wx.YES_NO | wx.ICON_WARNING)
            if popup.ShowModal() != wx.ID_YES: # User did not want to continue
                return


        for cookie in filenames:
            try:
                with open(os.path.join(pathname,
                                       filenames[cookie]),
                          "w",
                          newline="\n") as csvfile:

                    writer = csv.writer(csvfile,
                                        delimiter=',',
                                        quotechar='"',
                                        quoting=csv.QUOTE_MINIMAL)

                    writer.writerows(self.parser.get_cookies(cookie))
            except PermissionError: # Unable to write to cookie file
                self.show_message("Could not export cookies",
                                  "Could not export cookies because access\
was denied to {}.\n(You probably have it open in another program)".format(filenames[cookie]),
                                  wx.ICON_ERROR)
                return

        self.show_message("Cookies exported", "Successfully exported cookies", wx.ICON_INFORMATION)

    def on_process(self, _):
        """
        When the process button is clicked
        """
        self.parser = cookie_parser.get_cookie_fetcher(self.get_browser_name(),
                                                       self.setting_file_input.Value)

        if self.parser.error is not None:
            self.show_message("Error opening file", str(self.parser.error), wx.ICON_ERROR)
            return
        # Get all domains
        domains = self.parser.get_domains()
        domains.sort()

        # Clear the domain dropdown
        self.setting_view_domain.Clear()

        # Then add each domain option to the dropdown
        for domain in domains:
            self.setting_view_domain.Append(domain)

        # Enable the output section of the UI
        self.output_frame.Enable(True)

        message_template = "Found {} GA cookies over {} domains"

        message = message_template.format(self.parser.get_cookie_count(), len(domains))

        self.status_bar.SetStatusText(message)
        self.show_message("Successfully opened cookies database", message, wx.ICON_INFORMATION)

    def on_browse_path(self, _):
        """
        When the Input File setting's Browse button is clicked
        """
        with wx.FileDialog(self, "Open cookies file",
                           wildcard=BROWSER_FILETYPES[self.get_browser_name()],
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dialog:

            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = file_dialog.GetPath()

            self.setting_file_input.SetValue(pathname)

    def on_about(self, _):
        """
        Shows the about dialog
        """

        # Show the dialog
        dlg = wx.MessageDialog(self,
                               "\
Google Analytics Cookie Parser is a forensic tool to find, parse and evaluate \
Google Analytics cookies.\n\nIt was developed by Patrick Beart and other \
contributors found at http://github.com/pbeart/google-analytics-cookie-parser \
\n\nWith thanks to Kevin Ripa, for being such an encouraging mentor to his \
students, without whom this tool would never have come about.",
                               "About GA Cookie Parser",
                               wx.ICON_NONE | wx.CENTRE)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def on_exit(self, _):
        """
        Called upon program being closed
        """
        self.Close(True)  # Close the frame.

APP = wx.App(False)
FRAME = MainWindow(None, "GA Cookie Parser")
APP.MainLoop()
