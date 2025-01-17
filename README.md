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
- [ ] **Expanded Dataset Views**:  
  Integrating more dataset columns for visualization and filtering.
    
- [ ] **Select District and School**  
  Users can pick a district and school, with the map centering on the chosen area.

- [ ] **Highlight Areas of Concern**  
  - Users can mark concern zones on the map by:
    - Clicking specific census blocks.
    - Drawing freeform shapes snapped to boundaries.
  - Capture and save these markings along with user identity.

- [ ] **Mark Feedback for Selected Zones**  
  For each marked area, users can:
    - Indicate confidence levels (low, medium, high).
    - Select predefined factors influencing the marking, with the ability to add custom reasons.

- [ ] **Enhanced School Information**  
  - Clicking a school will open a detailed view with additional contextual information.
     
- [ ] **Enhanced Map Features**:  
   - Adding a geographical underlay for Georgia with visible landmarks and main roads.
   - Displaying school zones and census blocks for enhanced clarity.

- [ ] **Improve Styling**  
  Enhance CSS for better user experience.

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
