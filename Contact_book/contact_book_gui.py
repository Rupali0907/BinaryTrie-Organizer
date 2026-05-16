import tkinter as tk
from tkinter import ttk, messagebox
from contact_book import ContactBook, load_from_file, save_to_file

class ContactBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Book")
        self.root.geometry("800x600")
        
        # Initialize contact book
        self.contact_book = load_from_file("contacts.json")
        
        # Create GUI elements
        self.create_widgets()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        # Frame for contact form
        form_frame = ttk.LabelFrame(self.root, text="Contact Details", padding=10)
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Name
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Phone
        ttk.Label(form_frame, text="Phone:").grid(row=1, column=0, sticky=tk.W)
        self.phone_entry = ttk.Entry(form_frame, width=30)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky=tk.W)
        self.email_entry = ttk.Entry(form_frame, width=30)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.add_button = ttk.Button(button_frame, text="Add", command=self.add_contact)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.update_button = ttk.Button(button_frame, text="Update", command=self.update_contact)
        self.update_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = ttk.Button(button_frame, text="Delete", command=self.delete_contact)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Search Frame
        search_frame = ttk.LabelFrame(self.root, text="Search Contacts", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_contacts)
        
        # Contacts Treeview
        self.tree_frame = ttk.LabelFrame(self.root, text="Contacts", padding=10)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.tree = ttk.Treeview(self.tree_frame, columns=("Name", "Phone", "Email"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Email", text="Email")
        
        self.tree.column("Name", width=200)
        self.tree.column("Phone", width=150)
        self.tree.column("Email", width=250)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind tree selection
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Populate tree with all contacts
        self.refresh_contacts()
    
    def refresh_contacts(self, contacts=None):
        self.tree.delete(*self.tree.get_children())
        if contacts is None:
            contacts = self.contact_book.view_all_contacts()
        
        for contact in contacts:
            self.tree.insert("", tk.END, values=(contact.name, contact.number, contact.email))
    
    def search_contacts(self, event=None):
        query = self.search_entry.get()
        if query:
            results = self.contact_book.search_contact(query)
            self.refresh_contacts(results)
        else:
            self.refresh_contacts()
    
    def on_tree_select(self, event):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, "values")
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, values[0])
            self.phone_entry.delete(0, tk.END)
            self.phone_entry.insert(0, values[1])
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, values[2])
    
    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())
    
    def add_contact(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if not name or not phone:
            messagebox.showerror("Error", "Name and Phone are required fields")
            return
        
        if self.contact_book.add_contact(name, phone, email):
            messagebox.showinfo("Success", "Contact added successfully")
            self.refresh_contacts()
            self.clear_form()
        else:
            messagebox.showerror("Error", "Failed to add contact")
    
    def update_contact(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a contact to update")
            return
        
        old_name = self.tree.item(selected, "values")[0]
        new_name = self.name_entry.get().strip()
        new_phone = self.phone_entry.get().strip()
        new_email = self.email_entry.get().strip()
        
        if not new_name or not new_phone:
            messagebox.showerror("Error", "Name and Phone are required fields")
            return
        
        if self.contact_book.update_contact(old_name, new_name, new_phone, new_email):
            messagebox.showinfo("Success", "Contact updated successfully")
            self.refresh_contacts()
            self.clear_form()
        else:
            messagebox.showerror("Error", "Failed to update contact")
    
    def delete_contact(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a contact to delete")
            return
        
        name = self.tree.item(selected, "values")[0]
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete {name}?"):
            if self.contact_book.delete_contact(name):
                messagebox.showinfo("Success", "Contact deleted successfully")
                self.refresh_contacts()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to delete contact")
    
    def on_closing(self):
        save_to_file(self.contact_book, "contacts.json")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactBookApp(root)
    root.mainloop()