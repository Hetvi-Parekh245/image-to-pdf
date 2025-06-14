import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, ttk
import img2pdf
import os
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD, DND_FILES

# select folder
def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        images = [os.path.join(folder,f) for f in os.listdir(folder) if f.lower().endswith(('.png','.jpg','.jpeg','.gif','.bmp','.tif','.webp','.avif'))]
        images.sort()
        if not images:
            messagebox.showwarning("Warning","No images found in this directory")
            return
        
        listbox.delete(0, tk.END)
        
        select_folder.folder = folder
        select_folder.images = images

        for img_file in images:
            listbox.insert(tk.END, os.path.basename(img_file))

        convert_button.config(state='normal')
        move_up.config(state='normal')
        move_down.config(state='normal')
        remove_file.config(state='normal')
        clear_all.config(state='normal')

        show_preview(0)
##

# Preview
def show_preview(index):
    """Displays preview of the image at specified index in listbox."""
    img_file = select_folder.images[index]
    img = Image.open(img_file)
    img = img.resize((200,200))
    photo = ImageTk.PhotoImage(img)

    preview.config(image=photo)
    preview.image = photo
##

# Event on selecting 
def on_select(evt):
    """Event handler when selecting a different file in Listbox."""
    w = evt.widget
    idxs = w.curselection()
    if idxs:
        show_preview(idxs[0])
##

# Adjust files up and down
def move_up_file():
    idx = listbox.curselection()
    if not idx or idx[0] == 0:
        return
    idx = idx[0]
    fname = select_folder.images.pop(idx)
    select_folder.images.insert(idx-1, fname)

    listbox.delete(0, tk.END)
    for f in select_folder.images:
        listbox.insert(tk.END, os.path.basename(f))
    listbox.select_set(idx-1)
##
def move_down_file():
    idx = listbox.curselection()
    if not idx or idx[0] == len(select_folder.images)-1:
        return
    idx = idx[0]
    fname = select_folder.images.pop(idx)
    select_folder.images.insert(idx+1, fname)

    listbox.delete(0, tk.END)
    for f in select_folder.images:
        listbox.insert(tk.END, os.path.basename(f))
    listbox.select_set(idx+1)
##

# Remove files
def remove_file():
    idx = listbox.curselection()
    if not idx:
        return
    idx = idx[0]
    select_folder.images.pop(idx)

    listbox.delete(0, tk.END)
    for f in select_folder.images:
        listbox.insert(tk.END, os.path.basename(f))
    
    if select_folder.images:
        show_preview(0)
    else:
        preview.config(image='')
        preview.image = None
        convert_button.config(state='disabled')
        move_up.config(state='disabled')
        move_down.config(state='disabled')
        remove_file.config(state='disabled')
        clear_all.config(state='disabled')
##

# Clear all files
def clear_all():
    select_folder.images = []
    listbox.delete(0, tk.END)
    preview.config(image='')
    preview.image = None
    convert_button.config(state='disabled')
    move_up.config(state='disabled')
    move_down.config(state='disabled')
    remove_file.config(state='disabled')
    clear_all.config(state='disabled')
##

# Covert images to PDF
def convert_to_pdf():
    folder = select_folder.folder
    images = select_folder.images

    output_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")], initialdir=folder,initialfile="output.pdf")
    if not output_file:
        return
    try:
        progress['value'] = 0
        root.update()

        total = len(images)
        with open(output_file, "wb")as f:
            for i, img_file in enumerate(images):
                progress['value'] = int((i+1) / total * 100)
                root.update
            f.write(img2pdf.convert(images))
        
        progress['value'] = 100
        messagebox.showinfo("Success",f"PDF successfully created at {output_file}")
        status.config(text="Conversion finished.")
    except Exception as e:
        messagebox.showerror("Error",str(e))
        status.config(text=f"Error:{e}")
##

# Drop event 
def drop(event):
    files = root.tk.splitlist(event.data)
    files = [f for f in files if f.lower().endswith(('.png','.jpg','.jpeg','.gif','.bmp','.tif','.webp','.avif'))]

    if not files:
        return
    
    if not hasattr(select_folder,'images'):
        select_folder.images = []
    
    select_folder.images.extend(files)

    for f in files:
        listbox.insert(tk.END, os.path.basename(f))

    if files:
        show_preview(0)

    convert_button.config(state='normal')
    move_up.config(state='normal')
    move_down.config(state='normal')
    remove_file.config(state='normal')
    clear_all.config(state='normal')

    status.config(text=f"{len(files)} files added by drag-and-drop")

# Main GUI
root = TkinterDnD.Tk()

img = Image.open("pdf-logo.png")
img.save("pdf-logo.ico")

root.iconbitmap("pdf-logo.ico")
root.title("Image to PDF Converter")
root.geometry("500x700")
bg_color = "#ffcccb"
root.config(bg=bg_color)

label = tk.Label(root, text="Convert Your Images into one PDF", font=("Helvetica", 14), fg="#000000", bg=bg_color)
label.pack(pady=10)

frame = tk.Frame(root, bg=bg_color)
frame.pack(fill="both", expand=True, padx=20)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side="right", fill='y')

listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=('Helvetica',12))
listbox.pack(side='left', fill='both', expand=True)

listbox.bind('<<ListboxSelect>>',on_select)

listbox.drop_target_register(DND_FILES)
listbox.dnd_bind('<<Drop>>',drop)

scrollbar.config(command=listbox.yview)

select_button = tk.Button(root, text="Select Folder", command=select_folder, font=('Helvetica', 14))
select_button.pack(pady=10)

frame_buttons = tk.Frame(root, bg=bg_color)
frame_buttons.pack(pady=5)

move_up = tk.Button(frame_buttons, text="Move Up", command=move_up_file, state='disabled',width=10, height=1, font=('Helvetica',14,'bold'),bg="#A9EEE6")
move_up.grid(row=0, column=0, padx=5)

move_down = tk.Button(frame_buttons, text="Move Down", command=move_down_file, state='disabled',width=10,height=1,font=('Helvetica',14,'bold'),bg="#A9EEE6")
move_down.grid(row=0, column=1, padx=5)

remove_file = tk.Button(frame_buttons, text="Remove File", command=move_up_file, state='disabled', width=10, height=1, font=('Helvetica',14,'bold'),bg="#A9EEE6")
remove_file.grid(row=0, column=2, padx=5)

clear_all = tk.Button(root, text="Clear all", command=clear_all, font=('Helvetica', 14), state="disabled")
clear_all.pack(pady=15)

convert_button = tk.Button(root, text="Convert to PDF", command=convert_to_pdf, font=('Helvetica', 14), fg="red")
convert_button.pack()

label_preview = tk.Label(root, text="Preview", font=('Helvetica', 14, 'bold'), fg="#000000", bg=bg_color)
label_preview.pack(pady=10)

preview = tk.Label(root, bg=bg_color)
preview.pack()

progress = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
progress.pack(pady=10)

status = tk.Label(root, text="", font=('Helvetica',12), fg="#000000",bg=bg_color)
status.pack()

# Responsive GUI
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)



root.mainloop()
