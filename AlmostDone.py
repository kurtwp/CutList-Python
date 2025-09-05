
import tkinter as tk
from tkinter import messagebox, filedialog
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
import os

class WoodCuttingOptimizer(tk.Tk):
    """
    A desktop application for optimizing wood cutting using the Tkinter library.
    """
    BLADE_KERF = 0.125  # Blade thickness in inches

    def __init__(self):
        super().__init__()
        self.title("Wood Cutting Optimizer")
        self.geometry("800x800")
        self.cut_pieces = []
        self.boards = []
        self.stock_length = 0
        self.stock_width = 0

        self.create_widgets()

    def create_widgets(self):
        """Builds the GUI with improved styling and layout, including an exit button."""
        # Set a professional color scheme
        background_color = "#EFEFEF"  # Light gray
        frame_color = "#FDFDFD"       # Off-white for sections
        button_color = "#4CAF50"      # Green for action buttons
        label_color = "#333333"       # Dark gray for text

        self.config(bg=background_color)
        
        # Main container frame
        main_frame = tk.Frame(self, padx=20, pady=20, bg=background_color)
        main_frame.pack(expand=True, fill="both")

        # Title and description
        tk.Label(main_frame, text="Wood Cutting Optimizer", font=("Helvetica", 24, "bold"), bg=background_color, fg="#2E4053").pack(pady=(0, 5))
        tk.Label(main_frame, text="Cut calculations use a kerf (blade thickness) of 1/8 inch.", font=("Helvetica", 10, "italic"), bg=background_color, fg=label_color).pack(pady=(0, 20))

        # --- Stock Board Section ---
        stock_frame = tk.LabelFrame(main_frame, text="Stock Board Dimensions", font=("Helvetica", 12, "bold"), bg=frame_color, fg=label_color, padx=15, pady=10, relief="groove")
        stock_frame.pack(pady=10, fill="x")
        stock_frame_inner = tk.Frame(stock_frame, bg=frame_color)
        stock_frame_inner.pack()

        tk.Label(stock_frame_inner, text="Length (in.):", font=("Helvetica", 11), bg=frame_color, fg=label_color).grid(row=0, column=0, padx=5, pady=5)
        self.stock_length_entry = tk.Entry(stock_frame_inner, width=10)
        self.stock_length_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(stock_frame_inner, text="Width (in.):", font=("Helvetica", 11), bg=frame_color, fg=label_color).grid(row=0, column=2, padx=20, pady=5)
        self.stock_width_entry = tk.Entry(stock_frame_inner, width=10)
        self.stock_width_entry.grid(row=0, column=3, padx=5, pady=5)

        # --- Cut Piece Section ---
        piece_frame = tk.LabelFrame(main_frame, text="Cut Piece Details", font=("Helvetica", 12, "bold"), bg=frame_color, fg=label_color, padx=15, pady=10, relief="groove")
        piece_frame.pack(pady=10, fill="x")
        piece_frame_inner = tk.Frame(piece_frame, bg=frame_color)
        piece_frame_inner.pack()

        tk.Label(piece_frame_inner, text="Length (in.):", font=("Helvetica", 11), bg=frame_color, fg=label_color).grid(row=0, column=0, padx=5, pady=5)
        self.piece_length_entry = tk.Entry(piece_frame_inner, width=10)
        self.piece_length_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(piece_frame_inner, text="Width (in.):", font=("Helvetica", 11), bg=frame_color, fg=label_color).grid(row=0, column=2, padx=5, pady=5)
        self.piece_width_entry = tk.Entry(piece_frame_inner, width=10)
        self.piece_width_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(piece_frame_inner, text="Quantity:", font=("Helvetica", 11), bg=frame_color, fg=label_color).grid(row=0, column=4, padx=5, pady=5)
        self.quantity_entry = tk.Entry(piece_frame_inner, width=5)
        self.quantity_entry.grid(row=0, column=5, padx=5, pady=5)

        add_button = tk.Button(piece_frame_inner, text="Add Piece", command=self.add_piece, bg=button_color, fg="white", font=("Helvetica", 10, "bold"))
        add_button.grid(row=0, column=6, padx=(15, 5), pady=5)

        clear_button = tk.Button(piece_frame_inner, text="Clear All", command=self.clear_all, bg="#e74c3c", fg="white", font=("Helvetica", 10, "bold"))
        clear_button.grid(row=0, column=7, padx=5, pady=5)

        # --- Cut List Display ---
        tk.Label(main_frame, text="Cut List", font=("Helvetica", 14, "bold"), bg=background_color, fg="#2E4053").pack(pady=(10, 5))
        self.cut_list_display = tk.Text(main_frame, height=5, state="disabled", bg="#fcfcfc", relief="sunken")
        self.cut_list_display.pack(fill="x", pady=5)

        # --- Action Buttons ---
        button_frame = tk.Frame(main_frame, bg=background_color)
        button_frame.pack(pady=15)
        tk.Button(button_frame, text="Optimize Cuts", command=self.optimize_cuts, width=15, bg=button_color, fg="white", font=("Helvetica", 11, "bold")).pack(side="left", padx=10)
        tk.Button(button_frame, text="Export to PDF", command=self.export_pdf, width=15, bg="#3498db", fg="white", font=("Helvetica", 11, "bold")).pack(side="left", padx=10)
        
        # New Exit button
        tk.Button(button_frame, text="Exit", command=self.destroy, width=15, bg="#808B96", fg="white", font=("Helvetica", 11, "bold")).pack(side="left", padx=10)


        # --- Results and Canvas ---
        self.results_label = tk.Label(main_frame, text="", font=("Helvetica", 14, "bold"), bg=background_color, fg="#2E4053")
        self.results_label.pack(pady=(10, 5))
        
        # Scrollable Canvas
        canvas_frame = tk.Frame(main_frame, bg=background_color)
        canvas_frame.pack(expand=True, fill="both")
        
        self.canvas = tk.Canvas(canvas_frame, bg="white", borderwidth=1, relief="sunken")
        self.canvas.pack(side="left", expand=True, fill="both")

        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.config(yscrollcommand=scrollbar.set)
        
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        """Redraws the diagram when the window is resized."""
        if self.boards:
            self.draw_diagram(self.stock_length, self.stock_width, self.boards)

    def show_message(self, message, is_error=False):
        """Displays a message in a pop-up window."""
        if is_error:
            messagebox.showerror("Error", message)
        else:
            messagebox.showinfo("Info", message)

    def add_piece(self):
        """Adds a new piece to the cut list from user input."""
        try:
            length = float(self.piece_length_entry.get())
            width = float(self.piece_width_entry.get())
            quantity = int(self.quantity_entry.get())
            if length <= 0 or width <= 0 or quantity <= 0:
                self.show_message("Please enter positive values for length, width, and quantity.", True)
                return
            
            self.cut_pieces.append({"length": length, "width": width, "quantity": quantity})
            self.update_cut_list_display()
            
            self.piece_length_entry.delete(0, tk.END)
            self.piece_width_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
        except ValueError:
            self.show_message("Invalid input. Please enter numbers.", True)

    def update_cut_list_display(self):
        """Updates the text widget with the current cut list."""
        self.cut_list_display.config(state="normal")
        self.cut_list_display.delete("1.0", tk.END)
        for piece in self.cut_pieces:
            self.cut_list_display.insert(tk.END, f"{piece['quantity']} x {piece['length']}\" x {piece['width']}\"\n")
        self.cut_list_display.config(state="disabled")

    def clear_all(self):
        """Clears all inputs, lists, and the canvas."""
        self.stock_length_entry.delete(0, tk.END)
        self.stock_width_entry.delete(0, tk.END)
        self.piece_length_entry.delete(0, tk.END)
        self.piece_width_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.cut_pieces = []
        self.boards = []
        self.update_cut_list_display()
        self.results_label.config(text="")
        self.canvas.delete("all")

    def optimize_cuts(self):
        """
        Runs the optimization algorithm and draws the results.
        Uses a simplified shelf-packing algorithm with rotation logic.
        """
        try:
            self.stock_length = float(self.stock_length_entry.get())
            self.stock_width = float(self.stock_width_entry.get())
            if self.stock_length <= 0 or self.stock_width <= 0 or not self.cut_pieces:
                self.show_message("Please enter stock board dimensions and add pieces.", True)
                return
        except ValueError:
            self.show_message("Invalid stock board dimensions. Please enter numbers.", True)
            return

        all_pieces = []
        for item in self.cut_pieces:
            for _ in range(item["quantity"]):
                all_pieces.append({"length": item["length"], "width": item["width"]})
        
        # Sort pieces by area in descending order
        all_pieces.sort(key=lambda p: p["length"] * p["width"], reverse=True)

        self.boards = []
        total_waste = 0

        for piece in all_pieces:
            placed = False
            # Check if piece fits on any existing board
            for board in self.boards:
                # Try to place the piece on an existing shelf
                for shelf in board["shelves"]:
                    # Check for fit without rotation
                    can_fit = (piece["length"] + self.BLADE_KERF <= shelf["remaining_length"]) and \
                              (piece["width"] <= shelf["height"])
                    # Check for fit with rotation
                    can_fit_rotated = (piece["width"] + self.BLADE_KERF <= shelf["remaining_length"]) and \
                                      (piece["length"] <= shelf["height"])
                    
                    if can_fit:
                        shelf["pieces"].append(piece)
                        shelf["remaining_length"] -= (piece["length"] + self.BLADE_KERF)
                        placed = True
                        break
                    elif can_fit_rotated:
                        shelf["pieces"].append({"length": piece["width"], "width": piece["length"]})
                        shelf["remaining_length"] -= (piece["width"] + self.BLADE_KERF)
                        placed = True
                        break
                if placed:
                    break
                
                # If not placed on an existing shelf, try to create a new shelf on the current board
                
                # Check if the piece fits as-is
                if board["used_height"] + piece["width"] + self.BLADE_KERF <= self.stock_width and piece["length"] <= self.stock_length:
                    new_shelf = {
                        "height": piece["width"],
                        "remaining_length": self.stock_length - (piece["length"] + self.BLADE_KERF),
                        "pieces": [piece]
                    }
                    board["shelves"].append(new_shelf)
                    board["used_height"] += piece["width"] + self.BLADE_KERF
                    placed = True
                    break
                
                # Check if the piece fits when rotated
                if board["used_height"] + piece["length"] + self.BLADE_KERF <= self.stock_width and piece["width"] <= self.stock_length:
                    new_shelf = {
                        "height": piece["length"],
                        "remaining_length": self.stock_length - (piece["width"] + self.BLADE_KERF),
                        "pieces": [{"length": piece["width"], "width": piece["length"]}]
                    }
                    board["shelves"].append(new_shelf)
                    board["used_height"] += piece["length"] + self.BLADE_KERF
                    placed = True
                    break

            
            # If not placed on any existing board, create a new board
            if not placed:
                # Check if piece fits on a new, empty board
                if piece["width"] + self.BLADE_KERF <= self.stock_width and piece["length"] + self.BLADE_KERF <= self.stock_length:
                    new_board = {
                        "used_height": piece["width"] + self.BLADE_KERF,
                        "shelves": [{
                            "height": piece["width"],
                            "remaining_length": self.stock_length - (piece["length"] + self.BLADE_KERF),
                            "pieces": [piece]
                        }]
                    }
                    self.boards.append(new_board)
                # Check if rotated piece fits on a new, empty board
                elif piece["length"] + self.BLADE_KERF <= self.stock_width and piece["width"] + self.BLADE_KERF <= self.stock_length:
                    new_board = {
                        "used_height": piece["length"] + self.BLADE_KERF,
                        "shelves": [{
                            "height": piece["length"],
                            "remaining_length": self.stock_length - (piece["width"] + self.BLADE_KERF),
                            "pieces": [{"length": piece["width"], "width": piece["length"]}]
                        }]
                    }
                    self.boards.append(new_board)
                else:
                    self.show_message(f"Cannot cut piece {piece['length']}\" x {piece['width']}\" as it is too large for the stock board ({self.stock_length}\" x {self.stock_width}\").", True)
                    self.boards = []
                    self.canvas.delete("all")
                    return

        for board in self.boards:
            used_area = 0
            for shelf in board["shelves"]:
                # Calculate the used length of the shelf
                used_length_on_shelf = self.stock_length - shelf["remaining_length"]
                used_area += shelf["height"] * used_length_on_shelf
            
            board_area = self.stock_length * self.stock_width
            board["waste"] = board_area - used_area
            total_waste += board["waste"]

        self.results_label.config(text=f"Optimization Results: {len(self.boards)} Boards Used, Total Waste: {total_waste:.2f} sq. in.")
        self.draw_diagram(self.stock_length, self.stock_width, self.boards)

    def draw_diagram(self, stock_length, stock_width, boards):
        """Draws the cutting diagram on the canvas."""
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        padding = 50
        max_board_height = 300
        board_spacing = 20
        canvas_height = padding * 2 + len(boards) * max_board_height + (len(boards) - 1) * board_spacing
        self.canvas.config(height=canvas_height)
        scale = (canvas_width - padding * 2) / stock_length

        current_y = padding
        for i, board in enumerate(boards):
            x = padding
            y = current_y
            board_height_scaled = stock_width * scale

            self.canvas.create_rectangle(x, y, x + stock_length * scale, y + board_height_scaled,
                                         fill="#C2843A", outline="black")

            piece_y = y
            for shelf in board["shelves"]:
                piece_x = x
                for piece in shelf["pieces"]:
                    self.canvas.create_rectangle(piece_x, piece_y,
                                                 piece_x + piece["length"] * scale,
                                                 piece_y + piece["width"] * scale,
                                                 fill="#8B4513", outline="black")
                    self.canvas.create_text(piece_x + piece["length"] * scale / 2,
                                            piece_y + piece["width"] * scale / 2,
                                            text=f"{piece['length']}\"x{piece['width']}\"",
                                            fill="white", font=("Arial", 8))
                    
                    piece_x += piece["length"] * scale + self.BLADE_KERF * scale
                
                piece_y += shelf["height"] * scale + self.BLADE_KERF * scale
                
            used_height_scaled = board["used_height"] * scale
            waste_height_scaled = board_height_scaled - used_height_scaled
            if waste_height_scaled > 0:
                self.canvas.create_rectangle(x, y + used_height_scaled,
                                             x + stock_length * scale, y + board_height_scaled,
                                             fill="#A3B18A", outline="black")

            self.canvas.create_text(x, y - 10, anchor="w",
                                    text=f"Board {i + 1} - Waste: {board['waste']:.2f} sq. in.",
                                    font=("Arial", 12, "bold"))

            current_y += board_height_scaled + board_spacing
            
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def draw_diagram_on_pdf(self, c, stock_length, stock_width, boards, start_y):
        """Draws the entire cutting diagram on the ReportLab canvas."""
        padding = 0.5 * inch
        board_spacing = 0.25 * inch
        page_width, page_height = letter

        # Calculate scale factor
        scale_x = (page_width - 2 * padding) / stock_length
        scale_y = (page_width - 2 * padding) / stock_length  # Maintain aspect ratio for diagram

        current_y = start_y
        for i, board in enumerate(boards):
            board_width_scaled = stock_length * scale_x
            board_height_scaled = stock_width * scale_y
            
            # Check if a new page is needed
            if current_y - board_height_scaled - board_spacing < padding:
                c.showPage()
                current_y = page_height - padding
            
            x = padding
            y = current_y - board_height_scaled

            # Draw the full stock board rectangle
            c.setFillColorRGB(0.76, 0.52, 0.23) # Brown
            c.rect(x, y, board_width_scaled, board_height_scaled, fill=1, stroke=1)
            
            # Draw pieces on the board
            piece_y = y
            for shelf in board["shelves"]:
                piece_x = x
                for piece in shelf["pieces"]:
                    c.setFillColorRGB(0.55, 0.27, 0.07) # Darker brown
                    c.rect(piece_x, piece_y, piece["length"] * scale_x, piece["width"] * scale_y, fill=1, stroke=1)
                    
                    c.setFillColorRGB(1, 1, 1)
                    c.setFont("Helvetica", 8)
                    c.drawString(piece_x + piece["length"] * scale_x / 2 - c.stringWidth(f"{piece['length']}\"x{piece['width']}\"", "Helvetica", 8) / 2,
                                 piece_y + piece["width"] * scale_y / 2 - 3,
                                 f"{piece['length']}\"x{piece['width']}\"")
                    
                    piece_x += piece["length"] * scale_x + self.BLADE_KERF * scale_x
                
                piece_y += shelf["height"] * scale_y + self.BLADE_KERF * scale_y
            
            # Draw waste area
            used_height_scaled = board["used_height"] * scale_y
            waste_height_scaled = board_height_scaled - used_height_scaled
            if waste_height_scaled > 0:
                c.setFillColorRGB(0.64, 0.69, 0.54)
                c.rect(x, y + used_height_scaled, board_width_scaled, waste_height_scaled, fill=1, stroke=1)

            # Label for the board and its waste
            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x, y + board_height_scaled + 5, f"Board {i + 1} - Waste: {board['waste']:.2f} sq. in.")

            current_y = y - board_spacing
            
        return current_y

    def export_pdf(self):
        """Generates a PDF report from the optimization results and diagram."""
        if not self.boards:
            self.show_message("Please run the optimization first to generate a report.", True)
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Export Report to PDF"
        )
        if not file_path:
            return

        c = pdf_canvas.Canvas(file_path, pagesize=letter)
        y = letter[1] - inch * 0.5 # Starting y position, with top margin

        # Add title
        c.setFont("Helvetica-Bold", 18)
        c.drawString(inch * 0.5, y, "Wood Cutting Optimization Report")
        y -= inch * 0.5

        # Add input summary
        c.setFont("Helvetica", 12)
        c.drawString(inch * 0.5, y, f"Stock Board: {self.stock_length}\" x {self.stock_width}\"")
        y -= 0.25 * inch
        c.drawString(inch * 0.5, y, "Cut Pieces:")
        y -= 0.25 * inch
        for item in self.cut_pieces:
            c.drawString(inch * 0.75, y, f"    - {item['quantity']} x {item['length']}\" x {item['width']}\"")
            y -= 0.25 * inch
        y -= 0.25 * inch

        # Add optimization results
        c.setFont("Helvetica-Bold", 12)
        results_text = self.results_label.cget("text")
        c.drawString(inch * 0.5, y, results_text)
        y -= 0.5 * inch

        # Draw all diagrams
        self.draw_diagram_on_pdf(c, self.stock_length, self.stock_width, self.boards, y)
            
        c.save()
        self.show_message(f"PDF report saved to {file_path}")

    def save_cut_list(self):
        """Saves the current cut list to a JSON file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save Cut List"
        )
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(self.cut_pieces, f, indent=4)
            self.show_message("Cut list saved successfully!")

    def load_cut_list(self):
        """Loads a cut list from a JSON file."""
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Load Cut List"
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.cut_pieces = json.load(f)
                self.update_cut_list_display()
                self.show_message("Cut list loaded successfully!")
            except (json.JSONDecodeError, FileNotFoundError):
                self.show_message("Failed to load file. Please select a valid JSON file.", True)

if __name__ == "__main__":
    app = WoodCuttingOptimizer()
    app.mainloop()

