import tkinter as tk
from tkinter import ttk
import visualize_tools as vt
import control
import pandas as pd
from csv_reader import *
from tkinter import messagebox


class Window(tk.Tk):
    """ Concreate window
    """

    def init(self):
        super().__init__()


class MenuFrame(Window):
    """The main menu"""

    def __init__(self, old: tk.Tk | None = None) -> None:
        """Init the menu

        Args:
            old (tk.Tk | None, optional): The previous window. Defaults to None.
        """
        super().__init__()
        self.title("Main Program")
        self.title_font = ("consolus", 25)
        self.normal_font = ("consolus", 16)
        self.preference_list = ListDatabase("prefered_list")
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        self.old = old
        self.backend = control.Control()

    def init_components(self) -> None:
        """init the components
        """
        # Create a menu
        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="exit", command=self.destroy)

        self.frame = tk.Frame(self)
        self.geometry(
            f'{int(self.winfo_screenwidth()*0.5)}x{int(self.winfo_screenheight()*0.5)}')
        self.frame.pack(fill=tk.BOTH, expand=True, side="right")
        self.frame2 = tk.Frame(self)
        self.frame2.pack(fill=tk.BOTH, expand=True, side="right")
        # Label
        self.label = self.make_label("Menu")
        self.label.pack(anchor="center")
        # menu's button
        self.button_scatter_win = self.make_button(
            self.frame, "Data Story Telling", self.button_scatter)
        self.button_exploration_win = self.make_button(
            self.frame, "Get a show recommendation", self.button_exploration)
        self.button_preference_win = self.make_button(
            self.frame, "Edit your preference shows", self.button_preference)
        self.button_scatter_win.pack(anchor="center", side="top")
        self.button_preference_win.pack(anchor="center", side="top")
        self.button_exploration_win.pack(anchor="center", side="top")
        self.button_preference_win.pack(anchor="center", side="top")

        # create a bar graph
        self.bar_data = self.backend.count_unique(self.backend.data, "Genres")
        self.bar_graph = vt.BarGraph(
            self.frame2, self.bar_data[0], self.bar_data[1], "Count of each genre", lambda x: x)
        self.bar_graph.start()
        self.bar_graph.pack(expand=True, fill="both", side="left")

    def make_label(self, name: str) -> tk.Label:
        """create a lable

        Args:
            name (str): _description_

        Returns:
            tk.Label: _description_
        """
        _label = tk.Label(self.frame, text=name, font=self.title_font)
        _label.configure(justify="center")
        return _label

    def make_frame(self, parent: tk.Frame | tk.Tk) -> tk.Frame:
        frame = tk.Frame(parent)

    def make_button(self, parent: tk.Frame | tk.Tk, name: str, command) -> tk.Frame:
        """Create a button

        Args:
            parent (tk.Frame | tk.Tk): The parent
            name (str): The name of the button
            command (function): THe command of the button

        Returns:
            tk.Frame: a frame containing a button
        """
        button = tk.Button(parent, text=name, command=command)
        return button

    def button_scatter(self, *args):
        """Leads to the scatterplot window"""
        scatter = ScatterWindow(self)
        scatter.run()

    def button_exploration(self, *args):
        """Leads to the data exploration window"""
        if self.preference_list.data == []:
            messagebox.showwarning(
                "Cannot open that window.", "Please add a show into the preference list.")
            return
        exploration = DataExploration(self)
        exploration.run()

    def button_preference(self, *args):
        """Leads to the edit preference window
        """
        preference = PreferenceShows(self)
        preference.run()

    def run(self) -> None:
        """Run the window"""
        if not self.old is None:
            self.old.destroy()
        self.init_components()
        self.mainloop()


class ScatterWindow(Window):
    def __init__(self, old_window: tk.Tk) -> None:
        """init

        Args:
            old_window (tk.Tk): The old window
        """
        super().__init__()
        self.title("Data Story telling")
        self.old = old_window
        self.font = ("consolus", 25)
        self.backend = control.Control()
        self.title_font = ("consolus", 25)
        self.normal_font = ("consolus", 16)
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)

    def init_components(self):
        """init_the_components
        """
        # nav bar
        self.menu.add_command(label="Back", command=self.back_handler)

        self.right_frame = tk.Frame(self)
        self.geometry(
            f'{int(self.winfo_screenwidth()*0.5)}x{int(self.winfo_screenheight()*0.5)}')
        self.scatter = vt.ScatterChart(self)
        self.entry = vt.EntryTextView(self)
        self.scatter.display(*tuple(self.backend.get_scatter_plot()))
        self.scatter.pack(side="left", expand=True, fill="both")
        _key = tuple(self.backend.get_unique_genre() + ["All genres"])
        self.option = self.make_option_menu(
            self.right_frame, "All genres", _key)
        self.option.pack(side='top', fill='x')
        self.entry.pack(side="top", expand=True, fill="both")
        self.right_frame.pack(side="left")
        self.entry.display(self.create_descriptive(
            *tuple(self.backend.get_scatter_plot())))
        # bind the menu bar
        self.option_value.trace_add('write', self.change_in_menu)

    def make_option_menu(self, parent: tk.Frame | tk.Tk, default_text: str, values: tuple) -> tk.OptionMenu:
        """Create an option menu

        Args:
            parent (tk.Frame | tk.Tk): The parent of the newly created option menu.
            default_text (str): The initial displaying text of the option menu.
            values (tuple): The values to choose of the option menu.

        Returns:
            tk.OptionMenu: The option menu itself.
        """

        self.option_value = tk.StringVar(parent)
        self.option_value.set(default_text)
        option = tk.OptionMenu(self, self.option_value, *values)
        return option

    def change_in_menu(self, *args):
        """Update the scatter plot and the descriptive statistic"""
        value = self.option_value.get()
        if value == "All genres":
            value = None
        scatter_plot_data = self.backend.get_scatter_plot(value)
        self.scatter.update(*tuple(scatter_plot_data))
        self.entry.display(self.create_descriptive(*tuple(scatter_plot_data)))

    def create_descriptive(self, score: pd.Series, dropr: pd.Series):
        des1 = score.describe()
        des2 = dropr.describe()
        key1 = des1.keys()
        key2 = des2.keys()
        return ["-----Score-----"] + [f"{i} : {des1[i]}" for i in key1] + ["-----Drop Rate-----"] + [f"{i} : {des2[i]}" for i in key2] + ["-----Correlation-----", f"Correlation : {score.corr(dropr)}"]

    def back_handler(self, *args):
        """The back nav bar handler
        """
        menu_frame = MenuFrame(self)
        menu_frame.run()

    def run(self):
        """Run the whole thing
        """
        self.old.destroy()
        self.init_components()
        self.mainloop()


class DataExploration(Window):
    def __init__(self, old_window: tk.Tk):
        """Initialize

        Args:
            old_window (tk.Tk): The previous window.
        """
        super().__init__()
        self.title("Data Exploration")
        self.old = old_window
        self.title_font = ("consolus", 25)
        self.normal_font = ("consolus", 16)
        self.backend = control.Control()
        self.filters_list = []
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        self.remove_item = None

    def init_components(self):
        """Initialize the components
        """
        # nav bar
        self.menu.add_command(label="Back", command=self.back_handler)

        # Create a title label
        self.label = tk.Label(self, font=self.title_font,
                              text="Show Recommendation Page")
        self.label.pack(anchor="center", side="top")

        # Make the window big enough
        self.geometry(
            f'{int(self.winfo_screenwidth()*0.5)}x{int(self.winfo_screenheight()*0.5)}')

        # create all frames
        self.main_frame = tk.Frame(self)
        self.left_frame = tk.Frame(self.main_frame)
        self.right_frame = tk.Frame(self.main_frame)
        self.upper_right_frame = tk.Frame(self.right_frame)
        self.lower_right_frame = tk.Frame(self.right_frame)
        self.chooser_frame = tk.Frame(self.upper_right_frame)
        self.button_frame = tk.Frame(self.upper_right_frame)

        # create a histogram
        self.histogram = vt.Histogram(self.left_frame)

        # create a filter bar and buttons
        self.filter_screen = vt.TreeView(
            self.upper_right_frame, ("Type of filter", "Attribute", "Value"))
        self.type1_option, self.type1_value = self.make_option_menu(
            self.chooser_frame, "Inclusive", ["Inclusive", "Exclusive"])
        self.type2_option, self.type2_value = self.make_option_menu(
            self.chooser_frame, "Genres", ["Genres", "Episodes", "Type"])
        self.type3_option, self.type3_value = self.make_option_menu(
            self.chooser_frame, "Action", self.backend.get_unique_genre())
        self.type4_option, self.type4_value = self.make_option_menu(
            self.chooser_frame, "", ["1", "2"])
        self.type4_option.configure(state="disabled")
        self.add_button = tk.Button(
            self.button_frame, text="Add filter", command=self.add_button_handler)
        self.delete_button = tk.Button(
            self.button_frame, text="Delete", command=self.delete_button_handler)
        self.go_button = tk.Button(
            self.button_frame, text="Search", comman=self.search_button_handler)

        # create a pie chart
        self.select_pie, self.select_pie_value = self.make_option_menu(
            self.lower_right_frame, "Type", ("Type", "Genres"))
        self.pie = vt.PieChart(self.lower_right_frame)

        # packing
        self.main_frame.pack(expand=True, side="top", fill="both")
        self.left_frame.pack(expand=True, side="left", fill="both")
        self.right_frame.pack(expand=True, side="left", fill="both")
        self.type1_option.pack(expand=True, side="left", fill="x")
        self.type2_option.pack(expand=True, side="left", fill="x")
        self.type3_option.pack(expand=True, side="left", fill="x")
        self.type4_option.pack(expand=True, side="left", fill="x")
        self.upper_right_frame.pack(expand=True, side="top", fill="both")
        self.lower_right_frame.pack(expand=True, side="top", fill="both")
        self.filter_screen.pack(expand=True, side="top", fill="both")
        self.chooser_frame.pack(expand=True, side="top")
        self.filter_screen.start()
        self.add_button.pack(expand=True, side="left")
        self.delete_button.pack(expand=True, side="left")
        self.go_button.pack(expand=True, side="left")
        self.button_frame.pack(expand=True, side="top", fill="both")
        self.histogram.pack(expand=True, side="top", fill="both")
        self.delete_button.configure(state="disabled")
        self.select_pie.pack(expand=True, side="left", fill="x")
        self.pie.pack(expand=True, side="top")

        # histogram show
        self.raw_data = self.backend.get_data_for_histogram_page()
        self.data = self.raw_data["Score"].to_list()
        self.histogram.show(self.data, 5, "The spread of the data",
                            self.histogram.onClick(self.histogram_clicked_handler))

        # show pie chart
        pie_data = self.backend.count_unique(self.raw_data, "Type")
        self.pie.display(pie_data[0], pie_data[1])
        self.pie.start()

        # binding
        self.type2_value.trace_add("write", self.type2_change_handler)
        self.filter_screen.bind(self.filter_bar_handler)
        self.select_pie_value.trace_add("write", self.pie_chooser_handler)

    def bind_chooser(self, event: tk.Event) -> None:
        """A function used to bind to the chooser.

        Args:
            event (tk.Event): the event from the bind function
        """

        # activate the button
        self.delete_button.configure(state="active")

        # Put the selected item into the selected item list
        try:
            item = self.filter_screen.tree.item(event.widget.selection()[0])
        except IndexError:
            # If item unselected, disable the button
            self.delete_button.configure(state="disabled")
            return
        for i in self.filters_list:
            if i == item["values"]:
                self.filters_list.remove(i)
                break

    def histogram_clicked_handler(self, bar_index: int, *args) -> None:
        """Display the window of shows.

        Args:
            bar_index (int): the index of the histogram
        """
        # Get the shows from each bar
        each_histogram_show = self.backend.get_the_show_from_each_histogram(
            bar_index, self.raw_data, 5).sort_values(by="Score", ascending=False)
        showlist = ShowList(self, each_histogram_show)
        showlist.run()

    def type2_change_handler(self, *args) -> None:
        """The type2 option handler
        """
        self.type3_value.set("")
        self.type3_option.configure(state="disabled")
        self.type4_value.set("")
        self.type4_option.configure(state="disabled")
        value = self.type2_value.get()
        if value == "Genres":
            self.type3_value.set("Action")
            self.type3_option.configure(state="normal")
            self.type3_option["menu"].delete(0, tk.END)
            for i in self.backend.get_unique_genre():
                command = tk._setit(self.type3_value, i)
                self.type3_option["menu"].add_command(label=i, command=command)
        elif value == "Type":
            self.type3_value.set("TV")
            self.type3_option.configure(state="normal")
            self.type3_option["menu"].delete(0, tk.END)
            for i in self.backend.get_unique_type():
                command = tk._setit(self.type3_value, i)
                self.type3_option["menu"].add_command(label=i, command=command)
        else:
            self.type3_value.set(0)
            self.type3_option.configure(state="normal")
            self.type4_value.set(0)
            self.type4_option.configure(state="normal")
            self.type3_option["menu"].delete(0, tk.END)
            self.type4_option["menu"].delete(0, tk.END)
            for i in range(300):
                command = tk._setit(self.type3_value, i)
                self.type3_option["menu"].add_command(label=i, command=command)
            for i in range(300):
                command = tk._setit(self.type4_value, i)
                self.type4_option["menu"].add_command(label=i, command=command)

    def add_button_handler(self, *args) -> None:
        """The button handler
        """
        _filters = [
            self.type1_value.get(),
            self.type2_value.get(),
            self.type3_value.get(),
            self.type4_value.get()
        ]
        for i in self.filters_list:
            if i[1] == "Episodes" and _filters[1] == "Episodes":
                messagebox.showerror(
                    'Error!', "Episodes filter already exists.")
                return
            if i[1::] == _filters[1::]:
                messagebox.showerror(
                    'Error!', "No duplicated filters allowed.")
                return

        if _filters[0] == "Exclusive" and _filters[1] == "Episodes":
            messagebox.showerror(
                'Error!', "Cannot use 'Exclusive' on 'Episodes'.")
            return
        self.filters_list.append(_filters)
        print(self.filters_list)
        self.__update_filter_screen()

    def delete_button_handler(self, *args) -> None:
        """Delete the selected item from the filter list"""
        print(self.remove_item["values"][2])
        if self.remove_item["values"][1] == "Episodes":
            for i in self.filters_list:
                if i[1] == "Episodes":
                    self.filters_list.remove(i)
                    self.__update_filter_screen()
                    return
        self.filters_list.remove(self.remove_item["values"])
        self.__update_filter_screen()

    def filter_bar_handler(self, event: tk.Event, *args) -> None:
        """When the filter bar is selected, the delete button is enabled.

        Args:
            event (tk.Event): The event
        """
        # activate the button
        self.delete_button.configure(state="active")

        # Put the selected item into the selected item list
        try:
            item = self.filter_screen.tree.item(event.widget.selection()[0])
            self.remove_item = item
        except IndexError:
            # If item unselected, disable the button
            self.delete_button.configure(state="disabled")
            return

    def search_button_handler(self, *args) -> None:
        """A search button handler"""
        self.__show_histogram()
        self.__update_pie()

    def __show_histogram(self):
        """(private) Show the histogram
        """
        self.raw_data = self.backend.get_data_for_histogram_page(
            self.filters_list)
        self.data = self.raw_data["Score"].to_list()
        self.histogram.update(5, self.data)

    def pie_chooser_handler(self, *args):
        """Handle the piechart chooser
        """
        self.__update_pie()

    def __update_pie(self):
        """Update the piechart
        """
        value = self.select_pie_value.get()
        pie_data = self.backend.count_unique(self.raw_data, value)
        self.pie.update(pie_data[0], pie_data[1])

    def make_option_menu(self, parent: tk.Frame, default_text: str, values: tuple) -> tuple:
        """Create an option menu

        Args:
            parent (tk.Frame): The frame it's in
            default_text (str): the default text
            values (tuple): The values to choose from

        Returns:
            tuple: The tuple of opton and optionvalue
        """
        option_value = tk.StringVar(parent)
        option_value.set(default_text)
        option = tk.OptionMenu(parent, option_value, *values)
        return option, option_value

    def __update_filter_screen(self):
        """Update filter screen"""
        _list = [[i[0], i[1], "between " + i[2] + "and" + i[3]]
                 if i[3] != "" else i for i in self.filters_list]
        self.filter_screen.display(_list)

    def back_handler(self, *args):
        """back nav bar handler"""
        menu_frame = MenuFrame(self)
        menu_frame.run()

    def run(self):
        """Run the thing"""
        self.old.destroy()
        self.init_components()
        self.mainloop()


class PreferenceShows(Window):
    """Let the user edit the preference shows"""

    def __init__(self, old_window: tk.Tk):
        super().__init__()
        self.title("Edit preference show")
        self.old = old_window
        self.prefered_list = ListDatabase("prefered_list")
        self.title_font = ("consolus", 25)
        self.normal_font = ("consolus", 16)
        self.backend = control.Control()
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)

    def init_components(self):

        # Nav bar
        self.menu.add_command(label="Back", command=self.back_handler)

        # create a label
        tk.Label(self, text="Edit your preference shows",
                 font=self.title_font).pack(side='top')

        # Make the window big enough
        self.geometry(
            f'{int(self.winfo_screenwidth()*0.5)}x{int(self.winfo_screenheight()*0.5)}')

        # create frames
        self.left_frame = tk.Frame(self)
        self.right_frame = tk.Frame(self)

        # create a search bar and chooser element
        self.string_var = tk.StringVar(self)
        self.string_var.trace_add("write", lambda name, index, mode,
                                  sv=self.string_var: self.change_in_entry_handler(self.string_var))
        self.search_bar = tk.Entry(
            self.right_frame, textvariable=self.string_var)
        self.chooser = vt.TreeView(self.right_frame, ("id", 'name'))
        self.shows = self.backend.get_show_from_part_of_name()

        # create a list view
        self.list_view = vt.EntryTextView(self.left_frame)

        # pack
        self.list_view.pack(side="top", fill="both",
                            expand=True, anchor="center")
        show_name_list = [self.backend.get_show_by_id(float(i))["Name"].to_list()[
            0] for i in self.prefered_list.data]
        self.list_view.display(
            ["The shows will be listed bellow.", "-----------------------"] + show_name_list)

        self.add_button = tk.Button(
            self.right_frame, text="Add / Delete", command=self.bind_button)

        self.search_bar.pack(expand=True, side="top", fill="x")
        self.chooser.pack(expand=True, side="top", fill="both")
        self.add_button.pack(expand=True, side="top", fill="both")
        self.add_button.configure(state="disabled")
        self.chooser.display(self.shows)
        self.chooser.start()

        self.left_frame.pack(side="left", expand=True, fill="both")
        self.right_frame.pack(side="left", expand=True, fill="both")

        # Bind
        self.chooser.bind(self.bind_chooser)

    def bind_chooser(self, event: tk.Event):
        """
        A method for binding the chooser tree.
        """
        # activate the button
        self.add_button.configure(state="active")

        # Put the selected item into the selected item list
        try:
            item = self.chooser.tree.item(event.widget.selection()[0])
        except IndexError:
            # If item unselected, disable the button
            self.add_button.configure(state="disabled")
            return
        self.selected_item = item["values"][0]

    def bind_button(self, *args):
        """bind the button"""
        item = self.chooser.tree.item(self.chooser.tree.selection()[0])
        # print("item: ", item["values"][0])
        # print(self.backend.get_show_by_id(float(item["values"][0]))["Name"].to_list()[0])
        if item["values"][0] in self.prefered_list.data:
            self.prefered_list.delete(item["values"][0])
        else:
            self.prefered_list.data.append(item["values"][0])
        self.prefered_list.save_data()

        # Update the show list
        show_name_list = [self.backend.get_show_by_id(float(i))["Name"].to_list()[
            0] for i in self.prefered_list.data]
        self.list_view.display(show_name_list)

    def change_in_entry_handler(self, str_var: tk.StringVar):
        """Detect the change in entry

        Args:
            str_var (tk.StringVar): String var
        """

        # Update self.shows the search bar chooser
        self.shows = self.backend.get_show_from_part_of_name(str_var.get())
        self.chooser.display(self.shows)

    def back_handler(self, *args):
        menu_frame = MenuFrame(self)
        menu_frame.run()

    def run(self):
        self.old.destroy()
        self.init_components()
        self.mainloop()


class ShowList(tk.Toplevel):
    """Display a list of shows, this will be initiated and use by the DataExploration window"""

    def __init__(self, master: tk.Tk, shows: pd.DataFrame):
        super().__init__(master)
        self.shows = shows
        self.title("Histogram's data")
        self.geometry(
            f'{int(self.winfo_screenwidth()*0.25)}x{int(self.winfo_screenheight()*0.5)}')
        self.init_components()

    def init_components(self):
        self.treeview = vt.TreeView(self, ("id", "name"))
        names = self.shows["Name"].to_list()
        ids = self.shows["MAL_ID"].to_list()
        data = [[ids[i], names[i]] for i in range(len(names))]
        self.treeview.display(data)
        self.treeview.start()
        self.treeview.pack(expand=True, side='top', fill="both")
        self.treeview.bind(self.click_event)

    def click_event(self, event: tk.Event, *args):
        """Click event handler

        Args:
            event (tk.Event): _description_
        """
        item = self.treeview.tree.item(event.widget.selection()[0])
        ShowWindow(self, float(item["values"][0])).run()

    def run(self):
        self.mainloop()


class ShowWindow(tk.Toplevel):
    """A window dedicated to one show"""

    def __init__(self, master: tk.Tk | tk.Toplevel, show_id: float):
        super().__init__(master)
        self.title_font = ("consolus", 25)
        self.normal_font = ("consolus", 16)
        self.backend = control.Control()
        self.show = self.backend.get_show_by_id(show_id)
        self.title(self.show["Name"].to_list()[0])
        self.init_components()

    def init_components(self):
        tk.Label(self, text=self.show["Name"].to_list()[
                 0], font=self.title_font).pack(anchor="center", side="top")
        view = vt.EntryTextView(self)
        text = [
            "Genre: " + self.show["Genres"].to_list()[0],
            "Origin: " + self.show["Genres"].to_list()[0],
            "Number of Episodes: " + str(self.show["Episodes"].to_list()[0]),
            "Rating: " + self.show["Rating"].to_list()[0],
            "Duration: " + self.show["Duration"].to_list()[0],
            "Type: " + self.show["Type"].to_list()[0],
            "Score: " + str(self.show["Score"].to_list()[0]),
            "Sypnopsis: " + self.show["sypnopsis"].to_list()[0],
        ]
        view.display(text)
        view.pack(fill="both", expand="True", side="top")

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    test = MenuFrame()
    test.run()
