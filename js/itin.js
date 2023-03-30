//load map and itinerary data
const resItin = await fetch("data/itin.json")
const resWorld = await fetch("data/world.json")

let itin = await resItin.json()
let borders = await resWorld.json()

//get size of container
let width = d3.select("#container").node().getBoundingClientRect().width
let height = d3.select("#container").node().getBoundingClientRect().height  

//add svg to container
let svg = d3.select("#container")
    .append("svg")
    .attr("width", width)
    .attr("height", height)

//initialize geo-orthographic projection 
let projection = d3.geoOrthographic()
    .scale(250)
    .center([0, 0])
    .rotate([0, -30])
    .translate([width / 2, height / 2])

//store initial scale
const initialScale = projection.scale()

//initialize path generator for the projection
let path = d3.geoPath().projection(projection)

//create projection background (a circle)
let globe = svg.append("circle")
    .attr("fill", "#000")
    .attr("stroke", "#000")
    .attr("stroke-width", "0.2")
    .attr("cx", width/2)
    .attr("cy", height/2)
    .attr("r", initialScale)

//create svg group
let map = svg.append("g")

//add country borders
map.append("g")
    .attr("class", "countries" )
    .selectAll("path")
    .data(borders.features)
    .enter().append("path")
    .attr("d", path)
    .attr("fill", "white")
    .style('stroke', 'black')
    .style('stroke-width', 0.35)

//plot points
const pinRadius = 1.3
svg.selectAll(null)
    .data(itin)
    .enter()
    .append("path")
    .each(function(d){
        d3.select(this).datum({type: 'Point', coordinates: [d.lon, d.lat]})
            .attr("d", path.pointRadius(pinRadius))
            .attr("fill", "red")
    })

//rotate
const sensitivity = 75
const speed = 200
const t = d3.timer(function(elapsed) {
    const rotate = projection.rotate()
    const k = sensitivity / projection.scale()
    projection.rotate([
        rotate[0] - 1 * k,
        rotate[1]
    ])
    path = d3.geoPath().projection(projection)
    svg.selectAll("path").attr("d", path.pointRadius(pinRadius))
}, speed)

//respond to drag
svg.call(d3.drag().on("drag", (event) => {
    const rotate = projection.rotate()
    const k = sensitivity / projection.scale()
    projection.rotate([
      rotate[0] + event.dx * k,
      rotate[1] - event.dy * k
    ])
    path = d3.geoPath().projection(projection)
    svg.selectAll("path").attr("d", path.pointRadius(pinRadius))
  }))

//respond to scale slider change
d3.select("#scaleSlider").on("change", function(d){
    projection.scale(this.value)
    globe.attr("r", this.value)
})

//respond to scale reset button click
d3.select("#scaleResetButton").on("click", function() {
    projection.scale(initialScale)
    globe.attr("r", initialScale)
    d3.select("#scaleSlider").property("value", initialScale)
})