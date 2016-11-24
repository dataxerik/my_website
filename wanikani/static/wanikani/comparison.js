kanjiLengthArr = [];

for(var property in kanjiJsonVar){
    kanjiLengthArr.push(kanjiJsonVar[property].length);
}

var w = 500;
var h = Math.max.apply(null, kanjiLengthArr) + 100;
var barPadding = 1;

console.log(h);

var svg = d3.select("body").append("svg").attr("width", w).attr("height", h);

svg.selectAll("rect")
   .data(kanjiLengthArr)
   .enter()
   .append("rect")
   .attr("x", function(d, i) {
       return i * (w /kanjiLengthArr.length);
   })
   .attr("y", function(d, i) {
       return h - (d);
   })
   .attr("width", w / kanjiLengthArr.length - barPadding)
   .attr("height", function(d) {
       return d;
   })
   .attr("fill", function(d) {
       return "rgb(0, 0, " + (d * 10) + ")";
   });