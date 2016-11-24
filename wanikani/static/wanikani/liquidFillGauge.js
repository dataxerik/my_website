function liquidFillGaugeDefaultSettings() {
    return {
        minValue: 0, // The gauge minimum value.
        maxValue: 100, // The gauge max value.
        circleThickness: 0.05, // The outer circle thickness as a % of its radius.
        circleFillGap: 0.05, // The size of the gap between the outer circle and wave circle as % of the outer circle.
        circleColor: "#178BCA", // The color of the outer circle.
        waveHeight: 0.05, // The wave height  as a % of the radius of the wave circle.
        waveCount: 1, // The number of full waves per width of the wave circle.
        waveRiseTime: 1000, // The amount of time in milliseconds for a full wave to rise from 0 to its final height.
        waveAnimateTime: 18000, // The amount of time in milliseconds for a full wave to enter the wave circle.
        waveRise: true, // Control if the wave should rise from 0 to its full height, or start at tis full height.
        waveHeightScaling: true, // Controls wave size scaling at low and high fill percentages, When true, wave height reaches it's maximum at 50% fill, and minimum at 0% and 100% fill. This helps to prevent the wave from making the wave circle from appear totally full or empty when near it's minimum or maximum fill.
        waveAnimate: true, // Controls if the wave scrolls or is static
        waveColor: "#178BCA", // The color of the fill wave.
        waveOffset: 0, // The amount to initially offset the wave. 0 = no offset, 1 = offset of one full wave.
        textVertPosition: .5, // The height at which to display the percentage text within the wave circle.
        textSize: 1, // The relative height of the text to display in th wave circle .1 = 50%.
        valueCountUp: true, // if true, the display value counts from 0 to its final value upon loading.
        displayPercent: true, // if true, a % symbol is displayed after the value.
        textColor: "#045681", // The color of the value text when the wave does not overlap it.
        waveTextColor: "#A4DBf8" // The color of the value text when the wave overlaps it.
    };
}

function loadLiquidFillGauge(elementId, value, config) {
    if(config == null) { config = liquidFillGaugeDefaultSettings(); }

    var gauge = d3.select("#" + elementId);
    var radius = Math.min(parseInt(gauge.style("width")), parseInt(gauge.style(height))) / 2;
    var locationX = parseInt(gauge.style("width")) / 2 - radius;
    var locationY = parseInt(gauge.style("height")) / 2 - radius;
    var fillPercent = Math.max(config.minValue, Math.min(config.maxValue, value)) / config.maxValue;

    var waveHeightScale;
    if(config.waveHeightScaling){
        waveHeightScale = d3.scale.linear()
            .range([0, config.waveHeight, 0])
            .domain([0, 50, 100]);
    } else {
        waveHeightScale = d2.scale.linear()
    }
}