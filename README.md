# CoSEA Dashboard

## **Notes**:
- I have a [Project Overview](https://github.com/users/linnerlek/projects/4) set up where I track work in progress.
- I loosely followed the implementation plan outlined in *CoSEA_workflow.pptx* and *Tiffany & Tai's Log Book*.

## Current Features
- **Plot Options**  
  Allows visualization of data through an overlay based on:
  - **Modality**: Schools by CS course delivery methods (in-person, virtual, hybrid, or none).
  - **Certification**: Highlights schools with and without extra CS-certified teachers.
  - **Disparity**: Maps disproportion indices for Asian, Black, Hispanic, and White students.
  
  Lets the user filter schools based on:
  - **School type**: (City, Suburb, Rural, Town)
- **Map Options**  
  Visualize data through map layers:
  - **School Zones**: Turn on and off School Districts.

## Requirements
- **Python**: This project requires Python (3.13 or higher). Install it from [python.org](https://www.python.org/downloads/).
- **Git LFS**: This repository uses [Git Large File Storage](https://git-lfs.com/) (LFS) due to the large size of the included data files.
  ```bash
  git lfs install
  ```

## How to Install
1. Clone the repository:
    ```bash
    git clone https://github.com/linnerlek/CoSEA-Dash.git
    ```
2. Ensure Git LFS is pulling the large data files:
  **If Git LFS is installed, this step is automatic**. Otherwise, after cloning the repository, run:
    ```bash
    git lfs pull
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Run the application:
    ```bash
    python3 app.py
    ```

5. Open the app in your browser:
    ```bash
    http://127.0.0.1:8050/
    ```