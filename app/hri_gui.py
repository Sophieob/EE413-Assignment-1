import tkinter as tk

CHOICES = {
    "1": ("CONVEYER 1", "conveyer_1"),
    "2": ("CONVEYER 2", "conveyer_2"),
    "b": ("BIN (REJECT)", "bin"),
}

class OperatorGUI:
    def __init__(self, root):
        self.root = root
        root.title("Produce Grading - Operator Panel")
        root.geometry("800x500") # Setting the window size 

        # Message for what the robot has found
        self.message = tk.Label(root, text="Waiting for robot...", font=("Aerial", 24, "bold"))
        self.message.pack(pady=20)

        # Buttons for each choice for user input
        buttons = tk.Frame(root)
        buttons.pack(expand=True)

        for row, (key, (label, destination)) in enumerate(CHOICES.items()):
            tk.Button(
                buttons,
                text=f"{label} [{key.upper()}]",
                font=("Aerial",20),
                width=22, height=2,
                command=lambda d=destination: self.choose(d),
            ).grid(row=row, column=0, pady=6)

            root.bind(key, lambda event, d=destination: self.choose(d))

        self.status = tk.Label(root, text="Stack A: 0 Stack B: 0 Rejected: 0", font=("Aerial",14))
        self.status.pack(side="bottom", pady=10)

        def choose(self,destination):
            print("Operator chose:", destination)
            self.message.config(text=f"Sending item to: {destination}")

if __name__ == "__main__":
    root = tk.Tk()
    OperatorGUI(root)
    root.mainloop()