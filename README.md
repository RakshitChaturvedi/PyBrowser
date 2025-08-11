# PyBrowser A Web Browser from Scratch in Python

A web browser and rendering engine built from the ground up in Python, using only the standard tkinter library for its graphical user interface. This project is an educational deep dive into the full web stack, from networking and protocol handling to HTML/CSS parsing, layout and rendering.

![Image](https://github.com/user-attachments/assets/4c673f96-307e-4e37-929e-1e550fb32ece)

## Core Features
- **Custom Rendering Engine:** Renders styled text and elements to the screen without relying on any pre-existing web engine libraries (like WebKit or Gecko).
- **HTML & CSS Parsing:** Features a from-scratch HTML parser that constructs a Document Object Model (DOM) tree, handling implicit and self-closing tags. The CSS parser supports descendant selectors, property inheritance, and sorts rules by cascade priority.
- **Layout Engine:** Implements a layout engine that distinguishes between **block** and **inline** elements, correctly handles word wrapping, and applies styles like font weight, size, and color.
- **Robust Networking:** Supports HTTP/HTTPS GET and POST requests, including a robust implementation for handling multi-step redirects.
- **Interactive GUI:** A full browser "chrome" built with Tkinter, featuring:
    - Multiple Tabs
    - An Address Bar
    - Back Button & History
    - Click and Keyboard Input Handling for Links and Forms
- **HTML Forms:** Capable of handling user input and submitting forms via POST requests.

---
## Technical Deep Dive

The browser is built as a series of distinct layers, each responsible for a different part of the rendering pipeline.

1.  **Networking (`url_loader.py`):** The browser makes direct socket calls to fetch web content. It handles both HTTP and HTTPS (via the `ssl` module). The request logic is a self-contained loop that correctly follows up to 10 redirects, parsing `Location` headers and establishing new connections as needed for different hosts.

2.  **Parsing (`html_parser.py`, `styles.py`):** Raw HTML is processed into a **DOM tree** by a custom parser. CSS—from both a default user-agent stylesheet and remote `<link>` tags—is parsed into a list of rules. The CSS parser supports tag selectors and descendant selectors (e.g., `div p span`).

3.  **Styling & Layout (`styles.py`, `layout.py`):** A **style tree** is created by recursively applying the sorted CSS rules to the DOM tree, handling property inheritance down the tree. The **layout engine** then traverses this styled tree, calculating the position and dimensions of each element. It features distinct `BlockLayout` and `LineLayout` modes to correctly handle element flow, word wrapping, and special elements like `<input>` and `<button>`.

4.  **Rendering (`gui.py`):** The final layout tree is traversed to create a **display list** of simple drawing commands (e.g., `DrawText`, `DrawRect`). The Tkinter canvas is then used as a primitive GPU to execute these commands, rendering the final page. The entire GUI is event-driven, handling mouse clicks and keyboard input to support scrolling, links, and form input.

---
## Getting Started

To run the browser, you will need Python 3.

1.  **Clone the repository:**
    ```bash
    git clone PyBrowser
    cd PyBrowser
    ```
2.  **(Optional) Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
3.  **Run the browser:**
    The browser is run as a module from the project's root directory. Pass a URL as a command-line argument.
    ```bash
    python -m src.browser https://browser.engineering/
    ```

---
## 🚀 Future Roadmap

This project is an ongoing exploration into how web technologies work. The next major goals are to continue building out the core components to support a more dynamic and modern web.

- **JavaScript Runtime:** The next major undertaking is to build a JavaScript engine, likely by studying an embeddable engine like **Duktape**. This will involve parsing and executing JS, and creating the critical **DOM bindings** to allow scripts to manipulate the page content.
- **Advanced Rendering & Layout:** Enhancing the rendering engine with features like animations, visual effects (e.g., `box-shadow`), and more sophisticated layout modes (like initial support for Flexbox or Grid).
- **Concurrency and Performance:** Improving performance by moving networking and layout operations into separate **threads**. This will prevent the UI from freezing while complex pages are loading and rendering, leading to a much smoother user experience.

