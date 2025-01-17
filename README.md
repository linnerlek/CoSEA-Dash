# CoSEA Dashboard

## Current Features:
- **Filter Options**:  
  - **Modality**: Visualizes schools based on CS course delivery modality (in-person, virtual, hybrid or none).  
  - **Certification**: Highlights schools with and without extra CS-certified teachers.  
  - **Disparity**: Maps disproportion indices for Asian, Black, Hispanic, and White students.

- **Suboptions**:  
  - Enables toggling school classifications under each filter option to refine the map view.  

- **Legend**:  
  - Provides a visual reference matching map icons and colors.  
  - Includes:  
    - Shapes (circle, triangle) to distinguish classifications.  
    - School counts and percentages for each filter option.

## Work in Progress:
- [ ] Adding a geographical underlay for Georgia.
- [ ] Adding the logic for viewing school zones.
- [ ] Refining hover information to show only relevant data.  
- [ ] **Feature:** Clicking on a school opens a detailed table with additional school information.  
- [ ] Adding all relevant data from the dataset as additional view options.  
- [ ] Improving CSS for styling and readability.

## How to Install:
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
