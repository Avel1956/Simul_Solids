class TorsionVisualizer {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.currentParams = null;
        this.currentDeformation = 0;
        this.autoDeformationScale = 1.0;  // Factor de escala automático
        
        this.resizeCanvas();
        this.setupCamera();
        
        window.addEventListener('resize', () => this.resizeCanvas());
        this.setupMouseControls();
        
        // Añadir paleta de colores para el mapa de calor
        this.stressColors = {
            min: [0, 0, 255],    // Azul para mínimo esfuerzo
            max: [255, 0, 0]     // Rojo para máximo esfuerzo
        };

        this.showOriginal = true;
        this.showDeformed = true;
        this.showStress = true;
        this.showGrid = true;
        this.showMeasurements = true;
        
        // Para las mediciones
        this.measurementLabels = [];
    }

    resizeCanvas() {
        const container = this.canvas.parentElement;
        this.canvas.width = container.clientWidth;
        this.canvas.height = container.clientHeight;
        this.render(this.currentParams, this.currentDeformation);
    }

    setupCamera() {
        this.camera = {
            rotationX: 20 * Math.PI / 180,
            rotationY: -30 * Math.PI / 180,
            rotationZ: 0,
            distance: 1000,
            zoom: 1.5
        };
        this.baseScale = 300;
    }

    setupMouseControls() {
        let isDragging = false;
        let previousX = 0;
        let previousY = 0;

        this.canvas.addEventListener('mousedown', (e) => {
            isDragging = true;
            previousX = e.clientX;
            previousY = e.clientY;
        });

        this.canvas.addEventListener('mousemove', (e) => {
            if (!isDragging) return;

            const deltaX = e.clientX - previousX;
            const deltaY = e.clientY - previousY;

            this.camera.rotationY += deltaX * 0.01;
            this.camera.rotationX += deltaY * 0.01;

            previousX = e.clientX;
            previousY = e.clientY;

            this.render(this.currentParams, this.currentDeformation);
        });

        this.canvas.addEventListener('mouseup', () => {
            isDragging = false;
        });

        this.canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const zoomFactor = e.deltaY > 0 ? 0.95 : 1.05;
            this.camera.zoom *= zoomFactor;
            
            this.camera.zoom = Math.max(0.5, Math.min(10, this.camera.zoom));
            
            this.render(this.currentParams, this.currentDeformation);
        });
    }

    project(point) {
        if (!point || typeof point.x === 'undefined' || typeof point.y === 'undefined' || typeof point.z === 'undefined') {
            console.error('Punto inválido:', point);
            return { x: 0, y: 0, scale: 1, depth: 0 }; // Valor por defecto
        }

        const cos = Math.cos;
        const sin = Math.sin;
        const {rotationX, rotationY, rotationZ} = this.camera;

        let x = point.x * this.baseScale * this.camera.zoom;
        let y = point.y * this.baseScale * this.camera.zoom;
        let z = point.z * this.baseScale * this.camera.zoom;

        // Rotaciones
        let temp = y;
        y = y * cos(rotationX) - z * sin(rotationX);
        z = temp * sin(rotationX) + z * cos(rotationX);

        temp = x;
        x = x * cos(rotationY) + z * sin(rotationY);
        z = -temp * sin(rotationY) + z * cos(rotationY);

        temp = x;
        x = x * cos(rotationZ) - y * sin(rotationZ);
        y = temp * sin(rotationZ) + y * cos(rotationZ);

        const perspective = 2000;
        const scale = perspective / (perspective + z + this.camera.distance);
        
        return {
            x: this.canvas.width/2 + x * scale,
            y: this.canvas.height/2 + y * scale,
            scale: scale,
            depth: z
        };
    }

    drawCylinder(params, deformation) {
        const {length, outerDiameter, segments} = params;
        
        const canvasAspect = this.canvas.width / this.canvas.height;
        const maxDimension = Math.max(length, outerDiameter * canvasAspect);
        this.baseScale = Math.min(this.canvas.width, this.canvas.height) / (maxDimension * 1.5);

        const radius = outerDiameter / 2;
        const segmentHeight = length / segments;
        const startZ = -length/2;

        const gridSize = 48;
        const surfacePoints = [];

        const maxTwistAngle = deformation * Math.PI;

        for (let i = 0; i <= segments; i++) {
            const z = startZ + (i * segmentHeight);
            const heightRatio = (z - startZ) / length;
            const rotation = maxTwistAngle * heightRatio;
            const row = [];

            for (let j = 0; j <= gridSize; j++) {
                const angle = (j / gridSize) * Math.PI * 2;
                const x = radius * Math.cos(angle);
                const y = radius * Math.sin(angle);
                
                const twistedX = x * Math.cos(rotation) - y * Math.sin(rotation);
                const twistedY = x * Math.sin(rotation) + y * Math.cos(rotation);
                
                row.push({
                    x: twistedX,
                    y: twistedY,
                    z: z,
                    angle: angle,
                    rotation: rotation
                });
            }
            surfacePoints.push(row);
        }

        this.drawSurface(surfacePoints);
        
        this.drawReferenceLines(surfacePoints);
        
        const numIndicators = 8;
        for (let i = 0; i <= numIndicators; i++) {
            const z = startZ + (i * length / numIndicators);
            const heightRatio = (z - startZ) / length;
            const rotation = maxTwistAngle * heightRatio;
            
            this.drawSectionIndicator({
                x: 0,
                y: 0,
                z: z,
                radius: radius,
                rotation: rotation,
                heightRatio: heightRatio
            });
        }

        this.drawTorsionIndicators(params, maxTwistAngle);
    }

    drawSurface(surfacePoints) {
        const quads = [];
        
        // Encontrar la rotación máxima para normalizar
        let maxRotation = 0;
        surfacePoints.forEach(row => {
            row.forEach(point => {
                maxRotation = Math.max(maxRotation, Math.abs(point.rotation));
            });
        });
        
        for (let i = 0; i < surfacePoints.length - 1; i++) {
            for (let j = 0; j < surfacePoints[i].length - 1; j++) {
                const p1 = surfacePoints[i][j];
                const p2 = surfacePoints[i][j + 1];
                const p3 = surfacePoints[i + 1][j + 1];
                const p4 = surfacePoints[i + 1][j];
                
                const centerZ = (p1.z + p2.z + p3.z + p4.z) / 4;
                const centerRotation = (p1.rotation + p2.rotation + p3.rotation + p4.rotation) / 4;
                
                quads.push({ 
                    points: [p1, p2, p3, p4], 
                    z: centerZ,
                    rotation: centerRotation,
                    normalizedRotation: Math.abs(centerRotation) / maxRotation
                });
            }
        }
        
        quads.sort((a, b) => b.z - a.z);
        
        for (const quad of quads) {
            const [p1, p2, p3, p4] = quad.points.map(p => this.project(p));
            
            // Color basado en la deformación normalizada
            const stressColor = this.getStressColor(quad.normalizedRotation);
            
            this.ctx.beginPath();
            this.ctx.moveTo(p1.x, p1.y);
            this.ctx.lineTo(p2.x, p2.y);
            this.ctx.lineTo(p3.x, p3.y);
            this.ctx.lineTo(p4.x, p4.y);
            this.ctx.closePath();

            // Relleno semi-transparente en azul
            this.ctx.fillStyle = `rgba(33, 150, 243, 0.1)`;
            this.ctx.fill();
            
            // Borde con color basado en la deformación
            this.ctx.strokeStyle = stressColor;
            this.ctx.lineWidth = 1;
            this.ctx.stroke();
        }
    }

    drawReferenceLines(surfacePoints) {
        if (!surfacePoints || !surfacePoints[0] || !surfacePoints[0].length) {
            console.error('surfacePoints inválidos:', surfacePoints);
            return;
        }

        const numLines = 16;
        for (let j = 0; j < surfacePoints[0].length; j += surfacePoints[0].length / numLines) {
            const startPoint = this.project(surfacePoints[0][Math.floor(j)]);
            if (!startPoint) continue;

            this.ctx.beginPath();
            this.ctx.moveTo(startPoint.x, startPoint.y);

            let maxRotation = 0;
            surfacePoints.forEach(row => {
                if (row[Math.floor(j)]) {
                    maxRotation = Math.max(maxRotation, Math.abs(row[Math.floor(j)].rotation));
                }
            });

            for (let i = 1; i < surfacePoints.length; i++) {
                if (!surfacePoints[i] || !surfacePoints[i][Math.floor(j)]) continue;
                
                const point = this.project(surfacePoints[i][Math.floor(j)]);
                if (!point) continue;

                this.ctx.lineTo(point.x, point.y);
                
                const normalizedRotation = Math.abs(surfacePoints[i][Math.floor(j)].rotation) / maxRotation;
                this.ctx.strokeStyle = this.getStressColor(normalizedRotation);
                this.ctx.stroke();
                
                this.ctx.beginPath();
                this.ctx.moveTo(point.x, point.y);
            }
        }
    }

    drawTorsionIndicators(params, deformation) {
        const {length} = params;
        const arrowSize = length * 0.1;
        
        this.drawArrow(
            {x: 0, y: 0, z: length/2},
            arrowSize,
            deformation > 0 ? 1 : -1
        );
        
        this.drawArrow(
            {x: 0, y: 0, z: -length/2},
            arrowSize,
            deformation > 0 ? -1 : 1
        );
    }

    drawArrow(center, size, direction) {
        const numPoints = 8;
        const radius = size;
        
        this.ctx.beginPath();
        for (let i = 0; i <= numPoints; i++) {
            const angle = (i / numPoints) * Math.PI * 2;
            const x = center.x + radius * Math.cos(angle);
            const y = center.y + radius * Math.sin(angle);
            const point = this.project({x, y, z: center.z});
            
            if (i === 0) {
                this.ctx.moveTo(point.x, point.y);
            } else {
                this.ctx.lineTo(point.x, point.y);
            }
        }
        
        this.ctx.strokeStyle = 'rgba(255, 0, 0, 0.7)';
        this.ctx.stroke();
        
        const arrowAngle = direction > 0 ? Math.PI/6 : -Math.PI/6;
        const arrowPoint = this.project({
            x: center.x + radius * Math.cos(arrowAngle),
            y: center.y + radius * Math.sin(arrowAngle),
            z: center.z
        });
        
        this.ctx.beginPath();
        this.ctx.moveTo(arrowPoint.x, arrowPoint.y);
        this.ctx.lineTo(arrowPoint.x + 10 * direction, arrowPoint.y);
        this.ctx.stroke();
    }

    drawSectionIndicator(section) {
        const { x, y, z, radius, rotation } = section;
        
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
        this.ctx.lineWidth = 1;
        this.drawCircle(x, z, radius * 1.2);

        const arcRadius = radius * 1.2;
        const points = [];
        const numPoints = 32;
        
        for (let i = 0; i <= numPoints; i++) {
            const t = i / numPoints;
            const angle = t * rotation;
            const px = x + arcRadius * Math.cos(angle);
            const py = y + arcRadius * Math.sin(angle);
            points.push(this.project({ x: px, y: py, z }));
        }

        if (points.length > 1) {
            this.ctx.beginPath();
            this.ctx.moveTo(points[0].x, points[0].y);
            for (let i = 1; i < points.length; i++) {
                this.ctx.lineTo(points[i].x, points[i].y);
            }
            
            const intensity = Math.abs(rotation) / Math.PI;
            this.ctx.strokeStyle = `rgba(255, 165, 0, ${0.7 + intensity * 0.3})`;
            this.ctx.lineWidth = 2;
            this.ctx.stroke();

            if (points.length > 2) {
                const lastPoint = points[points.length - 1];
                const prevPoint = points[points.length - 2];
                this.drawArrowhead(prevPoint, lastPoint, 8);
            }
        }

        const centerPoint = this.project({ x, y, z });
        const radialPoint = this.project({
            x: x + radius * Math.cos(rotation),
            y: y + radius * Math.sin(rotation),
            z: z
        });

        this.ctx.beginPath();
        this.ctx.moveTo(centerPoint.x, centerPoint.y);
        this.ctx.lineTo(radialPoint.x, radialPoint.y);
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
        this.ctx.lineWidth = 1;
        this.ctx.stroke();
    }

    drawArrowhead(from, to, size) {
        const angle = Math.atan2(to.y - from.y, to.x - from.x);
        const arrowAngle = Math.PI / 6;

        this.ctx.beginPath();
        this.ctx.moveTo(to.x, to.y);
        this.ctx.lineTo(
            to.x - size * Math.cos(angle - arrowAngle),
            to.y - size * Math.sin(angle - arrowAngle)
        );
        this.ctx.moveTo(to.x, to.y);
        this.ctx.lineTo(
            to.x - size * Math.cos(angle + arrowAngle),
            to.y - size * Math.sin(angle + arrowAngle)
        );
        this.ctx.stroke();
    }

    drawCircle(x, z, radius) {
        const points = [];
        const segments = 32;
        
        for (let i = 0; i <= segments; i++) {
            const angle = (i / segments) * Math.PI * 2;
            const px = x + radius * Math.cos(angle);
            const py = radius * Math.sin(angle);
            points.push(this.project({ x: px, y: py, z }));
        }

        this.ctx.beginPath();
        this.ctx.moveTo(points[0].x, points[0].y);
        for (let i = 1; i < points.length; i++) {
            this.ctx.lineTo(points[i].x, points[i].y);
        }
        this.ctx.closePath();
        this.ctx.stroke();
    }

    render(params = null, deformation = 0) {
        if (!params) {
            console.log('No hay parámetros para renderizar');
            return;
        }

        if (params) {
            this.currentParams = params;
            this.currentDeformation = deformation;
        }

        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        const renderParams = params || this.currentParams;
        const renderDeformation = params ? deformation : this.currentDeformation;
        
        if (renderParams) {
            // Dibujar estado original si está activado
            if (this.showOriginal) {
                this.ctx.globalAlpha = 0.3;
                this.drawCylinder(renderParams, 0);
                this.ctx.globalAlpha = 1.0;
            }

            // Dibujar estado deformado si está activado
            if (this.showDeformed) {
                this.drawCylinder(renderParams, renderDeformation);
            }

            // Dibujar mediciones si están activadas
            if (this.showMeasurements) {
                this.drawMeasurements(renderParams, renderDeformation);
            }
        }
    }

    drawAxes() {
        const length = 1.0;
        
        this.ctx.strokeStyle = '#ff0000';
        this.drawLine({x: 0, y: 0, z: 0}, {x: length, y: 0, z: 0});
        
        this.ctx.strokeStyle = '#00ff00';
        this.drawLine({x: 0, y: 0, z: 0}, {x: 0, y: length, z: 0});
        
        this.ctx.strokeStyle = '#0000ff';
        this.drawLine({x: 0, y: 0, z: 0}, {x: 0, y: 0, z: length});
    }

    drawLine(start, end) {
        const p1 = this.project(start);
        const p2 = this.project(end);
        this.ctx.beginPath();
        this.ctx.moveTo(p1.x, p1.y);
        this.ctx.lineTo(p2.x, p2.y);
        this.ctx.stroke();
    }

    setView(view) {
        switch (view) {
            case 'front':
                this.camera.rotationX = 0;
                this.camera.rotationY = 0;
                break;
            case 'side':
                this.camera.rotationX = 0;
                this.camera.rotationY = Math.PI / 2;
                break;
            case 'top':
                this.camera.rotationX = Math.PI / 2;
                this.camera.rotationY = 0;
                break;
        }
        this.render(this.currentParams, this.currentDeformation);
    }

    drawStressDistribution(params, deformation) {
        const {outerDiameter} = params;
        const radius = outerDiameter / 2;
        
        // Dibujar gradiente de esfuerzos en una sección transversal
        const sections = [0.25, 0.5, 0.75]; // Posiciones relativas donde mostrar esfuerzos
        sections.forEach(pos => {
            const z = -params.length/2 + params.length * pos;
            this.drawStressSection(0, z, radius, deformation * pos);
        });
    }

    drawStressSection(x, z, radius, rotation) {
        const segments = 32;
        const ctx = this.ctx;
        
        // Crear gradiente radial
        const center = this.project({x, y: 0, z});
        const gradient = ctx.createRadialGradient(
            center.x, center.y, 0,
            center.x, center.y, radius * this.baseScale * this.camera.zoom
        );
        
        gradient.addColorStop(0, 'rgba(0, 0, 255, 0.2)');
        gradient.addColorStop(1, 'rgba(255, 0, 0, 0.2)');
        
        ctx.fillStyle = gradient;
        // ... dibujar sección con gradiente
    }

    // Función para interpolar colores
    getStressColor(value) {
        // Asegurar que value está entre 0 y 1
        value = Math.max(0, Math.min(1, value));
        
        const r = this.stressColors.min[0] + (this.stressColors.max[0] - this.stressColors.min[0]) * value;
        const g = this.stressColors.min[1] + (this.stressColors.max[1] - this.stressColors.min[1]) * value;
        const b = this.stressColors.min[2] + (this.stressColors.max[2] - this.stressColors.min[2]) * value;
        
        return `rgb(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)})`;
    }

    // Método para permitir al usuario ajustar la escala manualmente
    setDeformationScale(scale) {
        this.userDefinedScale = true;
        this.autoDeformationScale = scale;
    }

    // Método para resetear a escala automática
    resetDeformationScale() {
        this.userDefinedScale = false;
        if (this.currentParams) {
            const {length, outerDiameter} = this.currentParams;
            this.autoDeformationScale = (outerDiameter / length) * 2;
        }
    }

    drawMeasurements(params, deformation) {
        const {length, outerDiameter} = params;
        const radius = outerDiameter / 2;
        
        // Limpiar etiquetas anteriores
        this.measurementLabels.forEach(label => label.remove());
        this.measurementLabels = [];

        // Mostrar ángulos de torsión en puntos clave
        const sections = [0.25, 0.5, 0.75];
        sections.forEach(pos => {
            const z = -length/2 + length * pos;
            const rotation = deformation * pos;
            const point = this.project({x: radius, y: 0, z: z});
            
            const label = document.createElement('div');
            label.className = 'measurement-label';
            label.textContent = `θ = ${(rotation * 180 / Math.PI).toFixed(1)}°`;
            label.style.left = `${point.x}px`;
            label.style.top = `${point.y}px`;
            
            this.canvas.parentElement.appendChild(label);
            this.measurementLabels.push(label);
        });

        // Actualizar leyenda de esfuerzos
        const maxStress = document.getElementById('maxStress');
        if (maxStress && this.calculator) {
            // Calcular el esfuerzo cortante máximo usando los parámetros correctos
            const maxShearStress = this.calculator.calculateMaxShearStress(
                params.torque,
                params.outerDiameter,
                params.innerDiameter
            );
            maxStress.textContent = `${(maxShearStress/1e6).toFixed(2)} MPa`;
        }
    }

    // Añadir método para establecer el calculator
    setCalculator(calculator) {
        this.calculator = calculator;
    }
} 