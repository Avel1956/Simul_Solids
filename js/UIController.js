class UIController {
    constructor(visualizer, calculator) {
        this.visualizer = visualizer;
        this.calculator = calculator;
    }

    initialize() {
        console.log('Inicializando UIController...'); // Debug
        this.bindInputs();
        this.bindButtons();
        this.bindControls();
        this.setupTheory();
        this.updateVisualization(); // Llamada inicial
    }

    bindInputs() {
        const inputs = [
            'length', 'outerDiameter', 'innerDiameter', 'segments',
            'elasticModulus', 'shearModulus', 'poissonRatio',
            'torque', 'deformationScale'
        ];

        inputs.forEach(id => {
            const element = document.getElementById(id);
            element.addEventListener('input', () => this.updateVisualization());
        });
    }

    bindButtons() {
        document.getElementById('reset').addEventListener('click', () => this.resetVisualization());
        document.getElementById('frontView').addEventListener('click', () => this.visualizer.setView('front'));
        document.getElementById('sideView').addEventListener('click', () => this.visualizer.setView('side'));
        document.getElementById('topView').addEventListener('click', () => this.visualizer.setView('top'));
    }

    bindControls() {
        // Controles de visualización
        document.getElementById('showOriginal').addEventListener('change', (e) => {
            this.visualizer.showOriginal = e.target.checked;
            this.updateVisualization();
        });
        
        document.getElementById('showDeformed').addEventListener('change', (e) => {
            this.visualizer.showDeformed = e.target.checked;
            this.updateVisualization();
        });
        
        document.getElementById('showStress').addEventListener('change', (e) => {
            this.visualizer.showStress = e.target.checked;
            this.updateVisualization();
        });
        
        document.getElementById('showGrid').addEventListener('change', (e) => {
            this.visualizer.showGrid = e.target.checked;
            this.updateVisualization();
        });
        
        document.getElementById('showMeasurements').addEventListener('change', (e) => {
            this.visualizer.showMeasurements = e.target.checked;
            this.updateVisualization();
        });
    }

    getInputValues() {
        return {
            length: parseFloat(document.getElementById('length').value) || 1.0,
            outerDiameter: parseFloat(document.getElementById('outerDiameter').value) || 0.1,
            innerDiameter: parseFloat(document.getElementById('innerDiameter').value) || 0,
            segments: parseInt(document.getElementById('segments').value) || 10,
            elasticModulus: parseFloat(document.getElementById('elasticModulus').value) || 200,
            shearModulus: parseFloat(document.getElementById('shearModulus').value) || 80,
            poissonRatio: parseFloat(document.getElementById('poissonRatio').value) || 0.3,
            torque: parseFloat(document.getElementById('torque').value) || 100,
            deformationScale: parseFloat(document.getElementById('deformationScale').value) || 1
        };
    }

    updateVisualization() {
        const params = this.getInputValues();
        console.log('Parámetros:', params); // Debug

        const results = this.calculator.calculateResults(params);
        console.log('Resultados:', results); // Debug
        
        // Actualizar visualización
        this.visualizer.render(params, params.deformationScale * results.twistAngle);
        
        // Actualizar resultados con los parámetros
        this.updateResults(results, params);
    }

    calculateStrainEnergy(params, results) {
        return 0.5 * params.torque * results.twistAngle;
    }

    updateResults(results, params) {
        console.log('Actualizando resultados...'); // Debug
        const resultsDiv = document.getElementById('results');
        console.log('ResultsDiv:', resultsDiv); // Debug

        if (!resultsDiv) {
            console.error('No se encontró el elemento de resultados');
            return;
        }

        if (!results) {
            console.error('No hay resultados para mostrar');
            return;
        }

        try {
            const html = `
                <p>Momento polar de inercia: ${results.polarMomentOfInertia.toExponential(3)} m⁴</p>
                <p>Esfuerzo cortante máximo: ${(results.maxShearStress/1e6).toFixed(2)} MPa</p>
                <p>Ángulo de torsión: ${results.twistAngleDegrees.toFixed(3)}°</p>
                <p>Deformación angular por unidad de longitud: ${(results.twistAngle/params.length).toFixed(5)} rad/m</p>
                <p>Energía de deformación: ${(0.5 * params.torque * results.twistAngle).toExponential(3)} J</p>
                <p>Rigidez torsional: ${(params.torque/results.twistAngle).toExponential(3)} N·m²</p>
            `;
            console.log('HTML a insertar:', html); // Debug
            resultsDiv.innerHTML = html;
        } catch (error) {
            console.error('Error al actualizar resultados:', error);
            console.error('Results:', results); // Debug
            console.error('Params:', params); // Debug
        }
    }

    resetVisualization() {
        const params = this.getInputValues();
        this.visualizer.render(params, 0);
    }

    setupTheory() {
        const equationContainer = document.querySelector('.equation-container');
        equationContainer.innerHTML = `
            <div class="equation">
                <h4>Momento Polar de Inercia (J)</h4>
                <p>J = (π/32)(D⁴ - d⁴)</p>
                <p class="equation-description">Donde D es el diámetro exterior y d es el diámetro interior</p>
            </div>
            <div class="equation">
                <h4>Esfuerzo Cortante Máximo (τ<sub>max</sub>)</h4>
                <p>τ<sub>max</sub> = (T·r)/J</p>
                <p class="equation-description">Donde T es el momento torsor, r es el radio exterior y J es el momento polar de inercia</p>
            </div>
            <div class="equation">
                <h4>Ángulo de Torsión (θ)</h4>
                <p>θ = (T·L)/(G·J)</p>
                <p class="equation-description">Donde T es el momento torsor, L es la longitud, G es el módulo de corte y J es el momento polar de inercia</p>
            </div>
        `;
    }
} 