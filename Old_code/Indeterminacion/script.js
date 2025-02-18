class CableAnalysis {
    constructor() {
        this.initializeElements();
        this.setupEventListeners();
        this.setupCanvas();
    }

    initializeElements() {
        // Elementos de entrada
        this.material1Select = document.getElementById('material1');
        this.material2Select = document.getElementById('material2');
        this.area1Input = document.getElementById('area1');
        this.area2Input = document.getElementById('area2');
        this.length1Input = document.getElementById('length1');
        this.length2Input = document.getElementById('length2');
        this.loadInput = document.getElementById('load');
        
        // Elementos de resultado
        this.stepsDiv = document.getElementById('step-by-step');
        this.forcesDiv = document.getElementById('forces');
        this.canvas = document.getElementById('diagram');
        this.ctx = this.canvas.getContext('2d');
    }

    setupEventListeners() {
        document.getElementById('calculate').addEventListener('click', () => this.calculate());
        document.getElementById('random').addEventListener('click', () => this.generateRandomExample());
        document.getElementById('step').addEventListener('click', () => this.showStepByStep());
        
        // Eventos para materiales personalizados
        this.material1Select.addEventListener('change', () => this.toggleCustomInput(1));
        this.material2Select.addEventListener('change', () => this.toggleCustomInput(2));
    }

    setupCanvas() {
        // Obtener el tamaño del contenedor
        const rect = this.canvas.getBoundingClientRect();
        
        // Configurar escala para dispositivos de alta resolución
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
        
        // Restablecer la transformación
        this.ctx.setTransform(1, 0, 0, 1, 0, 0);
        
        // Aplicar escala considerando el DPR
        this.ctx.scale(1, 1);
        
        // Mantener el tamaño visual
        this.canvas.style.width = `${rect.width}px`;
        this.canvas.style.height = `${rect.height}px`;
    }

    toggleCustomInput(cableNumber) {
        const select = document.getElementById(`material${cableNumber}`);
        const customDiv = document.getElementById(`custom${cableNumber}`);
        customDiv.style.display = select.value === 'custom' ? 'block' : 'none';
    }

    generateRandomExample() {
        // Generar valores aleatorios realistas
        this.area1Input.value = (Math.random() * 100 + 50).toFixed(2);
        this.area2Input.value = (Math.random() * 100 + 50).toFixed(2);
        this.length1Input.value = (Math.random() * 2 + 1).toFixed(2);
        this.length2Input.value = (Math.random() * 2 + 1).toFixed(2);
        this.loadInput.value = (Math.random() * 10000 + 5000).toFixed(0);
        
        this.calculate();
    }

    calculate() {
        // Obtener valores de entrada
        const data = this.getInputValues();
        
        // Validar entrada
        if (!this.validateInput(data)) return;

        // Realizar cálculos
        const results = this.performCalculations(data);

        // Mostrar resultados
        this.displayResults(results, data);
        
        // Actualizar visualización
        this.updateVisualization(data, results);
    }

    getInputValues() {
        return {
            E1: parseFloat(this.material1Select.value),
            E2: parseFloat(this.material2Select.value),
            A1: parseFloat(this.area1Input.value) * 1e-6, // convertir mm² a m²
            A2: parseFloat(this.area2Input.value) * 1e-6,
            L1: parseFloat(this.length1Input.value),
            L2: parseFloat(this.length2Input.value),
            P: parseFloat(this.loadInput.value)
        };
    }

    validateInput(data) {
        for (let value of Object.values(data)) {
            if (isNaN(value) || value <= 0) {
                alert('Por favor, ingrese valores válidos positivos en todos los campos.');
                return false;
            }
        }
        return true;
    }

    performCalculations(data) {
        // Cálculo de rigidez de cada cable
        const k1 = (data.E1 * data.A1) / data.L1;
        const k2 = (data.E2 * data.A2) / data.L2;

        // Cálculo de fuerzas
        const F1 = (data.P * k1) / (k1 + k2);
        const F2 = data.P - F1;

        // Cálculo de deformaciones
        const delta1 = F1 * data.L1 / (data.E1 * data.A1);
        const delta2 = F2 * data.L2 / (data.E2 * data.A2);

        return { k1, k2, F1, F2, delta1, delta2 };
    }

    displayResults(results, data) {
        const renderEquations = () => {
            if (window.MathJax) {
                MathJax.typesetPromise && MathJax.typesetPromise();
            }
        };

        // Mostrar resultados paso a paso
        this.stepsDiv.innerHTML = `
            <div class="solution-step">
                <h3>Paso 1: Definición de Rigideces</h3>
                <p>La rigidez de cada cable se calcula como k = EA/L:</p>
                <div class="equation">
                    \\[ k_1 = \\frac{E_1A_1}{L_1} = \\frac{${(data.E1/1e9).toFixed(0)} \\cdot 10^9 \\cdot ${(data.A1*1e6).toFixed(2)}}{${data.L1}} = ${results.k1.toExponential(2)} \\text{ N/m} \\]
                    \\[ k_2 = \\frac{E_2A_2}{L_2} = \\frac{${(data.E2/1e9).toFixed(0)} \\cdot 10^9 \\cdot ${(data.A2*1e6).toFixed(2)}}{${data.L2}} = ${results.k2.toExponential(2)} \\text{ N/m} \\]
                </div>
            </div>

            <div class="solution-step">
                <h3>Paso 2: Ecuación de Compatibilidad</h3>
                <p>El desplazamiento vertical es igual para ambos cables:</p>
                <div class="equation">
                    \\[ \\frac{F_1}{k_1} = \\frac{F_2}{k_2} \\]
                </div>
            </div>

            <div class="solution-step">
                <h3>Paso 3: Equilibrio de Fuerzas</h3>
                <p>La suma de fuerzas debe igualar la carga aplicada:</p>
                <div class="equation">
                    \\[ F_1 + F_2 = P = ${data.P.toFixed(2)} \\text{ N} \\]
                </div>
            </div>

            <div class="solution-step">
                <h3>Paso 4: Solución del Sistema</h3>
                <p>Combinando las ecuaciones anteriores:</p>
                <div class="equation">
                    \\[ F_1 = \\frac{P \\cdot k_1}{k_1 + k_2} = \\frac{${data.P.toFixed(2)} \\cdot ${results.k1.toExponential(2)}}{${results.k1.toExponential(2)} + ${results.k2.toExponential(2)}} = ${results.F1.toFixed(2)} \\text{ N} \\]
                    \\[ F_2 = \\frac{P \\cdot k_2}{k_1 + k_2} = \\frac{${data.P.toFixed(2)} \\cdot ${results.k2.toExponential(2)}}{${results.k1.toExponential(2)} + ${results.k2.toExponential(2)}} = ${results.F2.toFixed(2)} \\text{ N} \\]
                </div>
            </div>

            <div class="solution-step">
                <h3>Paso 5: Cálculo de Deformaciones</h3>
                <p>Las deformaciones en cada cable son:</p>
                <div class="equation">
                    \\[ \\Delta L_1 = \\frac{F_1L_1}{E_1A_1} = \\frac{${results.F1.toFixed(2)} \\cdot ${data.L1}}{${(data.E1/1e9).toFixed(0)} \\cdot 10^9 \\cdot ${(data.A1*1e6).toFixed(2)}} = ${(results.delta1 * 1000).toFixed(2)} \\text{ mm} \\]
                    \\[ \\Delta L_2 = \\frac{F_2L_2}{E_2A_2} = \\frac{${results.F2.toFixed(2)} \\cdot ${data.L2}}{${(data.E2/1e9).toFixed(0)} \\cdot 10^9 \\cdot ${(data.A2*1e6).toFixed(2)}} = ${(results.delta2 * 1000).toFixed(2)} \\text{ mm} \\]
                </div>
            </div>
        `;

        this.forcesDiv.innerHTML = `
            <div class="forces-summary">
                <h3>Resultados Finales</h3>
                <p>Cable 1: F₁ = ${results.F1.toFixed(2)} N (${((results.F1/data.P)*100).toFixed(1)}% de la carga)</p>
                <p>Cable 2: F₂ = ${results.F2.toFixed(2)} N (${((results.F2/data.P)*100).toFixed(1)}% de la carga)</p>
                <p>Deformación vertical: ${(results.delta1 * 1000).toFixed(2)} mm</p>
            </div>
        `;

        // Renderizar ecuaciones después de actualizar el contenido
        setTimeout(renderEquations, 100);
    }

    updateVisualization(data, results) {
        // Dibujar configuración inicial
        this.drawSystem(false);
        
        // Dibujar configuración deformada
        this.drawSystem(true, results.delta1, results.delta2);
        
        // Ajustar el canvas cuando cambie el tamaño de la ventana
        window.addEventListener('resize', () => {
            this.setupCanvas();
            this.drawSystem(false);
            this.drawSystem(true, results.delta1, results.delta2);
        });
    }

    drawSystem(isDeformed, delta1 = 0, delta2 = 0) {
        // Limpiar todo el canvas al inicio
        if (!isDeformed) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }

        // Obtener dimensiones del canvas
        const width = this.canvas.offsetWidth;
        const height = this.canvas.offsetHeight;
        
        // Obtener datos actuales
        const data = this.getInputValues();
        
        // Factor de escala para la visualización (pixels por metro)
        const scale = Math.min(width, height) * 0.2;
        
        // Configurar estilo
        this.ctx.strokeStyle = isDeformed ? '#2ecc71' : '#bdc3c7';
        this.ctx.lineWidth = isDeformed ? 2 : 1;
        
        // Calcular puntos de referencia
        const centerX = width / 2;
        const centerY = height * 0.6; // Mover el punto de referencia más abajo
        const barWidth = width * 0.3;
        const barHeight = 10;
        
        // Puntos de anclaje de los cables
        const leftAnchorX = centerX - barWidth / 2;
        const rightAnchorX = centerX + barWidth / 2;
        // Calcular desplazamiento vertical según las deformaciones
        const verticalDisp = isDeformed ? Math.min(delta1, delta2) * scale : 0;
        const barY = centerY + verticalDisp;
        
        // Puntos superiores de anclaje
        // Calcular posiciones de anclaje superior basadas en las longitudes reales
        const topY = centerY - Math.min(data.L1, data.L2) * scale;
        const topLeftX = leftAnchorX - (data.L1 * scale * 0.3);
        const topRightX = rightAnchorX + (data.L2 * scale * 0.3);
        
        // Dibujar puntos de anclaje superiores
        this.ctx.fillStyle = '#666';
        this.drawPoint(topLeftX, topY);
        this.drawPoint(topRightX, topY);
        
        // Dibujar líneas de referencia (verticales punteadas)
        if (!isDeformed) {
            this.ctx.setLineDash([5, 5]);
            this.ctx.beginPath();
            this.ctx.moveTo(leftAnchorX, topY);
            this.ctx.lineTo(leftAnchorX, barY);
            this.ctx.moveTo(rightAnchorX, topY);
            this.ctx.lineTo(rightAnchorX, barY);
            this.ctx.stroke();
            this.ctx.setLineDash([]);
        }
        
        // Dibujar cables
        this.ctx.setLineDash(isDeformed ? [] : [5, 5]);
        this.ctx.beginPath();
        // Cable izquierdo
        this.ctx.moveTo(topLeftX, topY);
        this.ctx.lineTo(leftAnchorX, barY);
        // Cable derecho
        this.ctx.moveTo(topRightX, topY);
        this.ctx.lineTo(rightAnchorX, barY);
        this.ctx.stroke();
        this.ctx.setLineDash([]);
        
        // Dibujar barra
        this.ctx.beginPath();
        this.ctx.rect(leftAnchorX, barY - barHeight/2, barWidth, barHeight);
        this.ctx.stroke();
        
        // Dibujar carga
        if (isDeformed) {
            const arrowLength = Math.min(30, data.P / 1000); // Escalar flecha según la carga
            this.ctx.beginPath();
            this.ctx.moveTo(centerX, barY + barHeight/2);
            this.ctx.lineTo(centerX, barY + barHeight/2 + arrowLength);
            this.ctx.stroke();
            
            // Flecha de la carga
            this.ctx.beginPath();
            this.ctx.moveTo(centerX - 10, barY + barHeight/2 + arrowLength - 10);
            this.ctx.lineTo(centerX, barY + barHeight/2 + arrowLength);
            this.ctx.lineTo(centerX + 10, barY + barHeight/2 + arrowLength - 10);
            this.ctx.stroke();
        }
        
        // Añadir puntos de anclaje en la barra
        this.ctx.fillStyle = isDeformed ? '#2ecc71' : '#bdc3c7';
        this.drawPoint(leftAnchorX, barY);
        this.drawPoint(rightAnchorX, barY);
        
        // Añadir etiquetas
        this.ctx.fillStyle = '#333';
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'center';
        if (!isDeformed) {
            this.ctx.fillText('Cable 1', topLeftX, topY - 10);
            this.ctx.fillText('Cable 2', topRightX, topY - 10);
            this.ctx.fillText(`P = ${data.P.toFixed(0)} N`, centerX, barY + barHeight/2 + 45);
            
            // Añadir longitudes
            this.ctx.font = '10px Arial';
            this.ctx.fillText(`L₁ = ${data.L1.toFixed(2)} m`, (topLeftX + leftAnchorX)/2 - 20, (topY + barY)/2);
            this.ctx.fillText(`L₂ = ${data.L2.toFixed(2)} m`, (topRightX + rightAnchorX)/2 + 20, (topY + barY)/2);
        }
    }

    drawPoint(x, y) {
        this.ctx.beginPath();
        this.ctx.arc(x, y, 4, 0, Math.PI * 2);
        this.ctx.fill();
    }

    showStepByStep() {
        // Mostrar explicación detallada del proceso de solución
        const explanation = `
            <div class="step-explanation">
                <h3>Proceso de Solución Detallado</h3>
                <ol>
                    <li>Determinamos la rigidez de cada cable usando k = EA/L</li>
                    <li>Aplicamos el principio de superposición</li>
                    <li>Usamos la compatibilidad de deformaciones</li>
                    <li>Resolvemos el sistema de ecuaciones resultante</li>
                </ol>
            </div>
        `;
        this.stepsDiv.innerHTML = explanation;
    }
}

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', () => {
    new CableAnalysis();
}); 