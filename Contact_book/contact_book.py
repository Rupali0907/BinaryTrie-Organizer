import json
from collections import defaultdict

class Contact:
    def __init__(self, name, number, email=""):
        self.name = name
        self.number = number
        self.email = email
    
    def __str__(self):
        return f"Name: {self.name}, Phone: {self.number}, Email: {self.email}"
    
    def __lt__(self, other):
        return self.name.lower() < other.name.lower()
    
    def __eq__(self, other):
        return self.name.lower() == other.name.lower()

class BSTNode:
    def __init__(self, contact):
        self.contact = contact
        self.left = None
        self.right = None

class TrieNode:
    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.is_end = False
        self.contacts = []

class ContactBook:
    def __init__(self):
        self.root_bst = None
        self.root_trie = TrieNode()
    
    # BST Operations
    def insert_bst(self, node, contact):
        if node is None:
            return BSTNode(contact)
        
        if contact < node.contact:
            node.left = self.insert_bst(node.left, contact)
        else:
            node.right = self.insert_bst(node.right, contact)
        
        return node
    
    def inorder_traversal(self, node, result):
        if node:
            self.inorder_traversal(node.left, result)
            result.append(node.contact)
            self.inorder_traversal(node.right, result)
    
    def delete_bst(self, root, name):
        if root is None:
            return root
        
        if name.lower() < root.contact.name.lower():
            root.left = self.delete_bst(root.left, name)
        elif name.lower() > root.contact.name.lower():
            root.right = self.delete_bst(root.right, name)
        else:
            if root.left is None:
                return root.right
            elif root.right is None:
                return root.left
            
            temp = self.min_value_node(root.right)
            root.contact = temp.contact
            root.right = self.delete_bst(root.right, temp.contact.name)
        
        return root
    
    def min_value_node(self, node):
        current = node
        while current.left is not None:
            current = current.left
        return current
    
    # Trie Operations
    def insert_trie(self, name, contact):
        node = self.root_trie
        for char in name.lower():
            node = node.children[char]
        node.is_end = True
        node.contacts.append(contact)
    
    def search_prefix(self, prefix):
        node = self.root_trie
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        
        contacts = []
        self._collect_contacts(node, prefix.lower(), contacts)
        return contacts
    
    def _collect_contacts(self, node, prefix, contacts):
        if node.is_end:
            contacts.extend(node.contacts)
        
        for char, child_node in node.children.items():
            self._collect_contacts(child_node, prefix + char, contacts)
    
    def delete_trie(self, name, contact):
        nodes = []
        node = self.root_trie
        
        # Track the path
        for char in name.lower():
            if char not in node.children:
                return False
            nodes.append((node, char))
            node = node.children[char]
        
        # Remove the contact
        if contact in node.contacts:
            node.contacts.remove(contact)
        
        # If no more contacts, mark as not end
        if not node.contacts:
            node.is_end = False
        
        # Clean up unused nodes
        for i in range(len(nodes)-1, -1, -1):
            parent, char = nodes[i]
            child = parent.children[char]
            if not child.children and not child.is_end:
                del parent.children[char]
            else:
                break
        
        return True
    
    # Public Interface
    def add_contact(self, name, number, email=""):
        contact = Contact(name, number, email)
        self.root_bst = self.insert_bst(self.root_bst, contact)
        self.insert_trie(name, contact)
        return True
    
    def search_contact(self, prefix):
        return self.search_prefix(prefix)
    
    def view_all_contacts(self):
        contacts = []
        self.inorder_traversal(self.root_bst, contacts)
        return contacts
    
    def delete_contact(self, name):
        # Find the contact in BST
        contacts = self.search_prefix(name)
        exact_match = None
        for contact in contacts:
            if contact.name.lower() == name.lower():
                exact_match = contact
                break
        
        if exact_match:
            # Delete from BST
            self.root_bst = self.delete_bst(self.root_bst, name)
            # Delete from Trie
            self.delete_trie(name, exact_match)
            return True
        return False
    
    def update_contact(self, old_name, new_name, new_number, new_email):
        if self.delete_contact(old_name):
            return self.add_contact(new_name, new_number, new_email)
        return False

def save_to_file(contact_book, filename):
    contacts = contact_book.view_all_contacts()
    data = [{"name": c.name, "number": c.number, "email": c.email} for c in contacts]
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_from_file(filename):
    contact_book = ContactBook()
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            for contact_data in data:
                contact_book.add_contact(
                    contact_data['name'],
                    contact_data['number'],
                    contact_data.get('email', "")
                )
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return contact_book
