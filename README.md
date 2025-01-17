# CoSEA Dashboard

## Overview
I loosely followed the implementation outlined in *CoSEA_workflow.pptx* and *Tiffany & Tai's Log Book*.

## Current Features
- **Filter Options**  
  Allows visualization of data based on:
  - **Modality**: Schools by CS course delivery methods (in-person, virtual, hybrid, or none).
  - **Certification**: Highlights schools with and without extra CS-certified teachers.
  - **Disparity**: Maps disproportion indices for Asian, Black, Hispanic, and White students.

- **Suboptions**  
  - Enables toggling school classifications under each filter option to refine the map view.

- **Map Interaction**  
  - Visualizes schools with distinct shapes and colors based on selected filters.
  - Integrates legends with icons and color references matching the map.  
  - Displays school counts and percentages for classifications.  

## Planned Features
I have a [Project](https://github.com/users/linnerlek/projects/4) set up where I track features and issues

## How to Install
1. Clone the repository:
    ```bash
    git clone https://github.com/linnerlek/CoSEA-Dash.git
    ```
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the application:
    ```bash
    python3 app.py
    ```
4. Open the app in your browser:
    ```bash
    http://127.0.0.1:8050/
    ```
