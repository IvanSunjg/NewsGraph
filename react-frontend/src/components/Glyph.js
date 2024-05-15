import * as d3 from "d3";
import d3tip from "d3-tip";

function RenderGlyph(GlyphList, svgRef, pos, maxLengthOfList) {

    function handleArcClick(event, d) {
        console.log(d);
    }

    const color_green = d3.scaleSequential(d3.interpolateGreens);
    const color_red = d3.scaleSequential(d3.interpolateReds);

    const maxHeight = GlyphList.length * 40;

    const svg = d3.select(svgRef.current)
        .attr("width", svgRef.current.clientWidth)
        .attr("height", maxHeight)
        .attr("style", "max-width: 100%; height: auto font: 10px sans-serif;");

    let positionY = -38;
    let positionX;
    if (pos === 0) {
        positionX = 30;
    } else {
        positionX = svgRef.current.clientWidth - 30;
    }


    const upperTriangles = svg.selectAll(".upper-triangle")
        .data(GlyphList)
        .enter()
        .append("path")
        .attr("id", (d) => `${d}`)
        .attr("d", (d) => {
            const t = d['supports'] + d['contradicts'] + 1;
            positionY += 40;
            if(pos === 0){
                return `M${positionX},${positionY} L${positionX + t / (maxLengthOfList + 1) * (svgRef.current.clientWidth - 60)},${positionY} L${positionX},${positionY + 20} z`;
            }else{
                return `M${positionX - t / (maxLengthOfList + 1) * (svgRef.current.clientWidth - 60)},${positionY} L${positionX},${positionY} L${positionX - t / (maxLengthOfList + 1) * (svgRef.current.clientWidth - 60)},${positionY + 20} z`;
            }
        })
        .attr("stroke", "black")
        .attr("fill", d => {
            if (d['supports'] === 0) {
                return "white"
            } else if (d['contradicts'] === 0) {
                return color_green(1)
            } else {
                return color_green(d['supports'] / (d['supports'] + d['contradicts']))
            }
        });

    positionY = -38;
    if (pos === 0) {
        positionX = 30;
    } else {
        positionX = svgRef.current.clientWidth - 30;
    }

    const lowerTriangles = svg.selectAll(".lower-triangle")
        .data(GlyphList)
        .enter()
        .append("path")
        .attr("d", (d) => {
            positionY += 40;
            const t = d['supports'] + d['contradicts'] + 1;
            if (pos === 0) {
                return `M${positionX + t / (maxLengthOfList + 1) * (svgRef.current.clientWidth - 60)},${positionY + 20} L${positionX + t / (maxLengthOfList + 1) * (svgRef.current.clientWidth - 60)},${positionY} L${positionX},${positionY + 20} z`;
            } else {
                return `M${positionX},${positionY + 20} L${positionX},${positionY} L${positionX - t / (maxLengthOfList + 1) * (svgRef.current.clientWidth - 60)},${positionY + 20} z`;
            }
        })
        .attr("stroke", "black")
        .attr("fill", d => {
            if (d['contradicts'] === 0) {
                return "white"
            } else if (d['supports'] === 0) {
                return color_red(1)
            } else {
                return color_red(d['contradicts'] / (d['supports'] + d['contradicts']))
            }
        });
    //     .on('mouseover', tooltip.show)
    //     .on('mouseout', tooltip.hide);

    return svg.node();
}

export default RenderGlyph;


// const tooltip = d3tip()
//     .style('border', 'solid 3px black')
//     .style('background-color', 'white')
//     .style('border-radius', '10px')
//     .style('float', 'left')
//     .style('font-family', 'monospace')
//     .html((event, d) => `
//   <div style='float: right'>
//     Claim:  <br/>
//   </div>`);

// svg.call(tooltip);
