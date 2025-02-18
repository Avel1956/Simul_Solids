class TorsionCalculator {
    constructor() {
        this.PI = Math.PI;
    }

    calculatePolarMomentOfInertia(outerDiameter, innerDiameter) {
        const ro = outerDiameter / 2;
        const ri = innerDiameter / 2;
        return (this.PI / 32) * (Math.pow(outerDiameter, 4) - Math.pow(innerDiameter, 4));
    }

    calculateMaxShearStress(torque, outerDiameter, innerDiameter) {
        const J = this.calculatePolarMomentOfInertia(outerDiameter, innerDiameter);
        const r = outerDiameter / 2;
        return (torque * r) / J;
    }

    calculateTwistAngle(torque, length, shearModulus, outerDiameter, innerDiameter) {
        const J = this.calculatePolarMomentOfInertia(outerDiameter, innerDiameter);
        // Convertir GPa a Pa
        const G = shearModulus * 1e9;
        return (torque * length) / (G * J);
    }

    getSegmentRotation(angle, segmentIndex, totalSegments) {
        return (angle * segmentIndex) / totalSegments;
    }

    calculateResults(params) {
        console.log('Calculando resultados...', params); // Debug
        
        const {
            length,
            outerDiameter,
            innerDiameter,
            shearModulus,
            torque
        } = params;

        // Convertir GPa a Pa
        const G = shearModulus * 1e9;
        
        // Calcular momento polar de inercia
        const J = (Math.PI / 32) * (Math.pow(outerDiameter, 4) - Math.pow(innerDiameter, 4));
        
        // Calcular ángulo de torsión en radianes
        const twistAngle = (torque * length) / (G * J);
        
        // Calcular esfuerzo cortante máximo
        const maxShearStress = (torque * (outerDiameter / 2)) / J;

        const results = {
            polarMomentOfInertia: J,
            twistAngle: twistAngle,
            twistAngleDegrees: (twistAngle * 180) / Math.PI,
            maxShearStress: maxShearStress
        };

        console.log('Resultados calculados:', results); // Debug
        return results;
    }
} 