import tkinter as tk
from tkinter import ttk
import random
import time
import statistics
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict

class InstructionScreen:
    def __init__(self, master, start_callback):
        self.master = master
        self.start_callback = start_callback
        
        self.master.title("Instructions")
        self.master.attributes('-fullscreen', True)
        
        self.lbl_instruction = tk.Label(master, text="Instructions:\n\nIn this test, you will see words displayed in different colors.\nYour task is to ignore the actual word and instead, select the color of the ink from the options provided.\n\nPress 'Start' when you are ready to begin.", font=("Helvetica", 24))
        self.lbl_instruction.pack(expand=True)
        
        self.btn_start = tk.Button(master, text="Start", command=self.start_countdown, font=("Helvetica", 24))
        self.btn_start.pack()
        
    def start_countdown(self):
        self.master.destroy()
        start_countdown_screen()

class CountdownScreen:
    def __init__(self, master, countdown_duration, countdown_callback):
        self.master = master
        self.countdown_duration = countdown_duration
        self.countdown_callback = countdown_callback
        
        self.master.title("Countdown")
        self.master.attributes('-fullscreen', True)
        
        self.lbl_countdown = tk.Label(master, text="", font=("Helvetica", 48))
        self.lbl_countdown.pack(expand=True)
        
        self.update_countdown(self.countdown_duration)
        
    def update_countdown(self, remaining_time):
        if remaining_time >= 0:
            self.lbl_countdown.config(text=str(remaining_time))
            self.master.after(1000, lambda: self.update_countdown(remaining_time - 1))
        else:
            self.master.destroy()
            self.countdown_callback()

class StroopTest:
    def __init__(self, master):
        self.master = master
        self.master.title("Stroop Test")
        self.master.attributes('-fullscreen', True)
        
        # Define colors and words
        self.colors = ["red", "green", "blue", "yellow", "brown", "black", "purple"]
        self.words = ["RED", "GREEN", "BLUE", "YELLOW", "BROWN", "BLACK", "PURPLE"]
        
        self.score = 0
        self.rounds = 0
        self.reaction_times = []
        self.start_time = None
        self.duration = 100  # Duration of the test in seconds
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        self.lbl_instruction = tk.Label(self.master, text="Select the color of the ink, not the word text", font=("Helvetica", 24))
        self.lbl_instruction.pack(pady=20)
        
        self.lbl_score = tk.Label(self.master, text="Score: 0 / {}".format(self.duration // 5), font=("Helvetica", 24))
        self.lbl_score.pack()
        
        self.lbl_result = tk.Label(self.master, text="", font=("Helvetica", 36), wraplength=800) # Adjust wraplength to ensure the sentence is within the visible area
        self.lbl_result.pack()
        
        self.var_answer = tk.StringVar(self.master)
        self.var_answer.set("")  # Default value
        
        self.choices_frame = tk.Frame(self.master)
        self.choices_frame.pack(pady=20)
        self.color_buttons = []
        for color in self.colors:
            btn = tk.Radiobutton(self.choices_frame, text=color.capitalize(), variable=self.var_answer, value=color, font=("Helvetica", 18), command=self.check_answer)
            btn.pack(side=tk.LEFT, padx=10)
            self.color_buttons.append(btn)
        
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.ax.set_xlabel('Trial')
        self.ax.set_ylabel('Reaction Time (s)')
        self.ax.set_title('Reaction Times')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, padx=20)
        
        self.table_frame = tk.Frame(self.master)
        self.table_frame.pack(side=tk.LEFT, padx=20)
        self.tree = ttk.Treeview(self.table_frame, columns=('Trial', 'Reaction Time (s)'), show='headings')
        self.tree.heading('Trial', text='Trial')
        self.tree.heading('Reaction Time (s)', text='Reaction Time (s)')
        self.tree.pack(side='left')
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient='vertical', command=self.tree.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        self.lbl_description = tk.Label(self.master, text="", font=("Helvetica", 16), wraplength=400, justify='left')
        self.lbl_description.pack(pady=20)

        self.lbl_set_necessary = tk.Label(self.master, text="Set Necessary", font=("Helvetica", 16))
        self.lbl_set_necessary.pack()

        self.start_test()
        
    def start_test(self):
        for btn in self.color_buttons:
            btn.config(state=tk.NORMAL)
        self.score = 0
        self.rounds = 0
        self.update_score()
        self.next_round()
        self.reaction_times = []
        self.start_time = time.time()
        self.master.after(self.duration * 1000, self.finish_test)  # Set a timer to finish the test
        
    def next_round(self):
        self.lbl_result.config(text="")
        if self.rounds < self.duration // 5:  # Approximately 2 minutes with 5-second rounds
            word = random.choice(self.words)
            color = random.choice(self.colors)
            self.lbl_result.config(text=word, fg=color)

    def check_answer(self):
        if self.start_time is not None:
            reaction_time = time.time() - self.start_time
            self.reaction_times.append(reaction_time)
            self.update_plot_single(len(self.reaction_times), reaction_time)
        user_answer = self.var_answer.get().upper()
        if user_answer == self.lbl_result.cget("fg").upper():
            self.score += 1
        self.update_score()
        self.next_round()  # Advance to the next round

    def update_score(self):
        self.lbl_score.config(text="Score: {} / {}".format(self.score, self.duration // 5))
        
    def finish_test(self):
        self.lbl_result.config(text="Test Finished. Your score is {} out of {}.".format(self.score, self.duration // 5))
        self.show_results()

    def show_results(self):
        reaction_times_dict = defaultdict(list)
        for i, time_val in enumerate(self.reaction_times, start=1):
            reaction_times_dict['Trial'].append(i)
            reaction_times_dict['Reaction Time (s)'].append(round(time_val, 2))
        
        # Calculate average reaction time
        average_reaction_time = round(statistics.mean(self.reaction_times), 2)
        
        # Update description text
        description_text = "Average Response Time: {} seconds\n\n".format(average_reaction_time)
        description_text += "The table below shows the reaction times for each trial.\n\n"
        description_text += "The graph displays the progression of reaction times over the trials."
        self.lbl_description.config(text=description_text)
        
        self.update_table(reaction_times_dict)
        self.update_plot(reaction_times_dict)
    
    def update_table(self, reaction_times_dict):
        self.tree.delete(*self.tree.get_children())
        for i in range(len(reaction_times_dict['Trial'])):
            self.tree.insert('', 'end', values=(reaction_times_dict['Trial'][i], reaction_times_dict['Reaction Time (s)'][i]))
        
    def update_plot_single(self, trial, reaction_time):
        self.ax.plot(trial, reaction_time, marker='o', linestyle='', color='blue')  # Plot individual reaction time
        self.ax.set_xlabel('Trial')
        self.ax.set_ylabel('Reaction Time (s)')
        self.ax.set_title('Reaction Times')
        self.canvas.draw()

    def update_plot(self, reaction_times_dict):
        self.ax.clear()
        self.ax.plot(reaction_times_dict['Trial'], reaction_times_dict['Reaction Time (s)'], marker='o', linestyle='-')
        self.ax.set_xlabel('Trial')
        self.ax.set_ylabel('Reaction Time (s)')
        self.ax.set_title('Reaction Times')
        self.canvas.draw()

def start_countdown_screen():
    root = tk.Tk()
    countdown_screen = CountdownScreen(root, 5, start_stroop_test)
    root.mainloop()

def start_stroop_test():
    root = tk.Tk()
    stroop_test = StroopTest(root)
    root.mainloop()

def main():
    root = tk.Tk()
    instruction_screen = InstructionScreen(root, start_countdown_screen)
    root.mainloop()

if __name__ == "__main__":
    main()
