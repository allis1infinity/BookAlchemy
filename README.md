# BookAlchemy

This is a simple web application created using Python and the **Flask** framework. The project allows you to manage a collection of books and authors.

### **Main Project Files**

* `app.py`: The main application file that contains the core logic.
* `data_models.py`: The file that defines the structure for the `Author` and `Book` database tables.
* `requirements.txt`: A list of all libraries required to run the project.
* `templates/`: The folder where all HTML files are stored.
* `data/`: The folder for the database file (`library.sqlite`).

---

### **How to Run the Project**
 
1.  Create a file named **`.env`** (with a dot at the start) in the project 
    root directory. Add your Flask secret key inside this file. This is 
    required for secure session management:
    ```
    # .env
    SECRET_KEY="your_very_secret_key_here"
    ```

2. Install the necessary libraries:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application: 
    ```bash
     python app.py
    ```
After launching, open your web browser and go to `http://127.0.0.1:5000/`.

"Create your own digital library by adding books and authors to your collection."