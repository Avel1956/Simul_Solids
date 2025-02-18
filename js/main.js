document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('torsionCanvas');
    if (!canvas) {
        console.error('Canvas no encontrado');
        return;
    }

    const calculator = new TorsionCalculator();
    const visualizer = new TorsionVisualizer(canvas);
    visualizer.setCalculator(calculator);
    const controller = new UIController(visualizer, calculator);
    
    controller.initialize();
});