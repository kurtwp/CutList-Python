import tkinter as tk
from tkinter import ttk, messagebox
import math

# A global list to store the pieces to be cut.
cut_pieces = []
BLADE_KERF = 0.125 # Kerf (blade thickness) in inches

# --- Functions for GUI actions ---

def show_message(message, message_type="info"):
    """Displays a message to the user."""
    message_label.config(text=message)
    if message_type == "error":
        message_label.config(foreground="red")
    else:
        message_label.config(foreground="green")
    
def add_piece():
    """Adds a new piece to the cut list based on user input."""
    try:
        length = float(piece_length_entry.get())
        width = float(piece_width_entry.get())
        quantity = int(quantity_entry.get())
        
        if length <= 0 or width <= 0 or quantity <= 0:
            show_message("Please enter valid length, width, and quantity.", "error")
            return

        cut_pieces.append({"length": length, "width": width, "quantity": quantity})
        update_cut_list_display()
        
        # Clear input fields
        piece_length_entry.delete(0, tk.END)
        piece_width_entry.delete(0, tk.END)
        quantity_entry.delete(0, tk.END)
        show_message("Piece added successfully.", "success")
        
    except ValueError:
        show_message("Invalid input. Please enter numbers.", "error")

def update_cut_list_display():
    """Updates the cut list display with the current pieces."""
    cut_list_display.delete(0, tk.END)
    for item in cut_pieces:
        cut_list_display.insert(tk.END, f"{item['quantity']} × {item['length']}\" × {item['width']}\"")
        
def clear_all():
    """Clears all input fields, the cut list, and the diagram."""
    stock_length_entry.delete(0, tk.END)
    stock_width_entry.delete(0, tk.END)
    piece_length_entry.delete(0, tk.END)
    piece_width_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)
    
    global cut_pieces
    cut_pieces = []
    update_cut_list_display()
    
    results_label.config(text="")
    diagram_canvas.delete("all")
    show_message("All fields cleared.", "success")
    
def optimize_cuts():
    """
    Performs the optimization and draws the cutting diagram.
    Uses a simplified shelf-packing algorithm.
    """
    try:
        stock_length = float(stock_length_entry.get())
        stock_width = float(stock_width_entry.get())
        
        if stock_length <= 0 or stock_width <= 0 or not cut_pieces:
            show_message("Please enter stock dimensions and add pieces.", "error")
            return

        all_pieces = []
        for item in cut_pieces:
            for _ in range(item["quantity"]):
                all_pieces.append({"length": item["length"], "width": item["width"]})
        
        # Sort pieces by area (descending) to optimize placement
        all_pieces.sort(key=lambda p: p["length"] * p["width"], reverse=True)

        boards = []
        total_waste = 0

        for piece in all_pieces:
            placed = False
            for board in boards:
                # Try to place the piece in an existing shelf
                for shelf in board["shelves"]:
                    can_fit = (piece["length"] + BLADE_KERF <= shelf["remaining_length"]) and \
                              (piece["width"] + BLADE_KERF <= shelf["height"])
                    can_fit_rotated = (piece["width"] + BLADE_KERF <= shelf["remaining_length"]) and \
                                      (piece["length"] + BLADE_KERF <= shelf["height"])
                    
                    if can_fit:
                        shelf["pieces"].append(piece)
                        shelf["remaining_length"] -= (piece["length"] + BLADE_KERF)
                        placed = True
                        break
                    elif can_fit_rotated:
                        shelf["pieces"].append({"length": piece["width"], "width": piece["length"]})
                        shelf["remaining_length"] -= (piece["width"] + BLADE_KERF)
                        placed = True
                        break
                
                if placed:
                    break
                
                # If not placed, try to create a new shelf on the current board
                new_shelf_height = piece["width"] + BLADE_KERF
                new_shelf_remaining_height = stock_width - board["used_height"]
                if new_shelf_height <= new_shelf_remaining_height:
                    new_shelf = {
                        "height": new_shelf_height,
                        "remaining_length": stock_length - (piece["length"] + BLADE_KERF),
                        "pieces": [piece]
                    }
                    board["shelves"].append(new_shelf)
                    board["used_height"] += new_shelf_height
                    placed = True
                    break

            # If not placed on any existing board, start a new one
            if not placed:
                new_board = {
                    "used_height": piece["width"] + BLADE_KERF,
                    "shelves": [{
                        "height": piece["width"] + BLADE_KERF,
                        "remaining_length": stock_length - (piece["length"] + BLADE_KERF),
                        "pieces": [piece]
                    }]
                }
                boards.append(new_board)

        # Calculate waste for each board and total waste
        for board in boards:
            board_area = stock_length * stock_width
            used_area = 0
            for shelf in board["shelves"]:
                used_area += (stock_length - shelf["remaining_length"]) * shelf["height"]
            board["waste"] = board_area - used_area
            total_waste += board["waste"]

        # Update the results display
        results_label.config(text=f"Boards Used: {len(boards)}\nTotal Waste: {total_waste:.2f} sq. in.")
        
        # Draw the diagram on the canvas
        draw_diagram(stock_length, stock_width, boards)
        
    except ValueError:
        show_message("Invalid stock board dimensions.", "error")

def draw_diagram(stock_length, stock_width, boards):
    """Draws the cutting diagram on the Tkinter canvas."""
    diagram_canvas.delete("all")
    
    # Calculate scale factor to fit within the canvas
    canvas_width = diagram_canvas.winfo_width()
    scale = (canvas_width - 50) / stock_length
    
    diagram_height = sum(300 + 10 for _ in boards) + 100
    diagram_canvas.config(height=diagram_height)

    y_offset = 25
    for i, board in enumerate(boards):
        x = 25
        y = y_offset + i * (stock_width * scale + 50)
        
        # Draw the full stock board rectangle
        diagram_canvas.create_rectangle(x, y, x + stock_length * scale, y + stock_width * scale,
                                        fill="#C2843A", outline="black")
        
        # Draw cut pieces
        current_y = y
        for shelf in board["shelves"]:
            current_x = x
            for piece in shelf["pieces"]:
                piece_width = piece["length"] * scale
                piece_height = piece["width"] * scale
                
                diagram_canvas.create_rectangle(current_x, current_y, current_x + piece_width, current_y + piece_height,
                                                fill="#8B4513", outline="black")
                
                # Add text for piece dimensions
                diagram_canvas.create_text(current_x + piece_width / 2, current_y + piece_height / 2,
                                           text=f"{piece['length']}\"x{piece['width']}\"", fill="white", font=("Inter", 8))
                
                # Draw kerf line
                current_x += piece_width
                diagram_canvas.create_rectangle(current_x, current_y, current_x + BLADE_KERF * scale, current_y + piece_height, fill="black", outline="")
                current_x += BLADE_KERF * scale
                
            current_y += shelf["height"] * scale
            
        # Draw the offcut area
        offcut_height = stock_width - board["used_height"]
        if offcut_height > 0:
            diagram_canvas.create_rectangle(x, y + board["used_height"] * scale, x + stock_length * scale, y + stock_width * scale,
                                            fill="#A3B18A", outline="black")
        
        # Add waste information
        diagram_canvas.create_text(x, y + stock_width * scale + 20,
                                   text=f"Board {i + 1} - Waste: {board['waste']:.2f} sq. in.",
                                   anchor="nw", font=("Inter", 10, "bold"))

# --- Main Window and Widgets ---

# Create the main window
root = tk.Tk()
root.title("Wood Cutting Optimizer")
root.geometry("800x600")

# Main frame
main_frame = ttk.Frame(root, padding="15")
main_frame.pack(fill=tk.BOTH, expand=True)

# Title
ttk.Label(main_frame, text="Wood Cutting Optimizer", font=("Inter", 24, "bold")).pack(pady=10)
ttk.Label(main_frame, text="Kerf (blade thickness) is 1/8 inch.", font=("Inter", 10, "italic")).pack()

# Message label for user feedback
message_label = ttk.Label(main_frame, text="", font=("Inter", 10), anchor="center")
message_label.pack(pady=5)

# Input frame for stock board
stock_frame = ttk.LabelFrame(main_frame, text="Stock Board", padding="10")
stock_frame.pack(fill=tk.X, pady=10)
stock_frame.columnconfigure(0, weight=1)
stock_frame.columnconfigure(1, weight=1)

ttk.Label(stock_frame, text="Length (in):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
stock_length_entry = ttk.Entry(stock_frame)
stock_length_entry.grid(row=0, column=1, sticky=tk.E, padx=5, pady=2)

ttk.Label(stock_frame, text="Width (in):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
stock_width_entry = ttk.Entry(stock_frame)
stock_width_entry.grid(row=1, column=1, sticky=tk.E, padx=5, pady=2)

# Input frame for cut pieces
piece_frame = ttk.LabelFrame(main_frame, text="Cut Pieces", padding="10")
piece_frame.pack(fill=tk.X, pady=10)
piece_frame.columnconfigure(0, weight=1)
piece_frame.columnconfigure(1, weight=1)
piece_frame.columnconfigure(2, weight=1)
piece_frame.columnconfigure(3, weight=1)

ttk.Label(piece_frame, text="Length:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
piece_length_entry = ttk.Entry(piece_frame)
piece_length_entry.grid(row=1, column=0, sticky=tk.EW, padx=5, pady=2)

ttk.Label(piece_frame, text="Width:").grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
piece_width_entry = ttk.Entry(piece_frame)
piece_width_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

ttk.Label(piece_frame, text="Quantity:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
quantity_entry = ttk.Entry(piece_frame)
quantity_entry.grid(row=1, column=2, sticky=tk.EW, padx=5, pady=2)

# Buttons for adding/clearing pieces
button_frame = ttk.Frame(piece_frame)
button_frame.grid(row=1, column=3, sticky=tk.EW, padx=5, pady=2)
ttk.Button(button_frame, text="Add Piece", command=add_piece).pack(side=tk.LEFT, fill=tk.X, expand=True)
ttk.Button(button_frame, text="Clear All", command=clear_all).pack(side=tk.LEFT, fill=tk.X, expand=True)

# Cut list display
ttk.Label(main_frame, text="Cut List", font=("Inter", 14, "bold")).pack(pady=5)
cut_list_display = tk.Listbox(main_frame, height=5)
cut_list_display.pack(fill=tk.X, pady=5)

# Optimize button
ttk.Button(main_frame, text="Optimize Cuts", command=optimize_cuts).pack(pady=10)

# Results label
results_label = ttk.Label(main_frame, text="", font=("Inter", 12))
results_label.pack(pady=5)

# Canvas for drawing the diagram
diagram_canvas = tk.Canvas(main_frame, bg="white", borderwidth=1, relief="solid")
diagram_canvas.pack(
