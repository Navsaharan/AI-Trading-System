// FamilyHVSDN User Management JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Firebase Auth
    initializeAuth();
    
    // Load initial user data
    loadUsers();
    
    // Setup event listeners
    setupEventListeners();
});

// Firebase Authentication
function initializeAuth() {
    firebase.auth().onAuthStateChanged(function(user) {
        if (!user) {
            window.location.href = '/login';
        }
    });
}

// Load Users
async function loadUsers() {
    try {
        const response = await fetch('/api/admin/users');
        const users = await response.json();
        
        const tableBody = document.getElementById('userTableBody');
        tableBody.innerHTML = ''; // Clear existing rows
        
        users.forEach(user => {
            const row = createUserRow(user);
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading users:', error);
        showError('Failed to load users');
    }
}

// Create User Row
function createUserRow(user) {
    const row = document.createElement('tr');
    
    row.innerHTML = `
        <td class="px-6 py-4 whitespace-nowrap">
            <div class="flex items-center">
                <div>
                    <div class="text-sm font-medium text-gray-900">${user.email}</div>
                    <div class="text-sm text-gray-500">${user.id}</div>
                </div>
            </div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${user.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                ${user.active ? 'Active' : 'Inactive'}
            </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
            ${user.role}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
            ${new Date(user.lastActive).toLocaleDateString()}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
            <button onclick="editUser('${user.id}')" class="text-indigo-600 hover:text-indigo-900 mr-4">Edit</button>
            <button onclick="deleteUser('${user.id}')" class="text-red-600 hover:text-red-900">Delete</button>
        </td>
    `;
    
    return row;
}

// Setup Event Listeners
function setupEventListeners() {
    // Add User Button
    document.getElementById('addUserBtn').addEventListener('click', () => {
        document.getElementById('addUserModal').classList.remove('hidden');
    });
    
    // Add User Form
    document.getElementById('addUserForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        
        try {
            const response = await fetch('/api/admin/users', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(Object.fromEntries(formData))
            });
            
            if (response.ok) {
                closeModal();
                loadUsers();
                showSuccess('User added successfully');
            } else {
                throw new Error('Failed to add user');
            }
        } catch (error) {
            console.error('Error adding user:', error);
            showError('Failed to add user');
        }
    });
}

// Edit User
async function editUser(userId) {
    // Implement edit user functionality
    console.log('Edit user:', userId);
}

// Delete User
async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/users/${userId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadUsers();
            showSuccess('User deleted successfully');
        } else {
            throw new Error('Failed to delete user');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        showError('Failed to delete user');
    }
}

// Modal Functions
function closeModal() {
    document.getElementById('addUserModal').classList.add('hidden');
    document.getElementById('addUserForm').reset();
}

// Utility Functions
function showSuccess(message) {
    // Implement toast or notification system
    alert(message);
}

function showError(message) {
    // Implement toast or notification system
    alert('Error: ' + message);
}
