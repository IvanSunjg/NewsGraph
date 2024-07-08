import * as d3 from "d3";

function RenderGlyph(GlyphList, svgRef, pos, maxLengthOfList) {

    const color_green = d3.scaleSequential(d3.interpolateGreens);
    const color_red = d3.scaleSequential(d3.interpolateReds);

    const svg = d3.select(svgRef.current)
        .attr("width", svgRef.current.clientWidth)
        

    let textPositionY = 10;
    let textPositionX = pos === 0 ? 10 : svgRef.current.clientWidth / 2 + 5;
    let glyphPositionX = pos === 0 ? svgRef.current.clientWidth / 2 + 5 : 5;

    for (let i = 0; i < GlyphList.length; i++) {

        const text = svg.append("text")
            .attr("class", "claim-text")
            .attr("x", textPositionX)
            .attr("y", textPositionY)
            .text("Claim: " + GlyphList[i]['claim'])
            .style("font-size", 13);

        const words = text.text().split(/\s+/).reverse();
        const lineHeight = 15;
        let lineNumber = 0;
        let line = [];
        let tspan = text.text(null)
            .append("tspan")
            .attr("x", textPositionX)
            .attr("y", textPositionY)
            .attr("dy", 0);

        while (words.length > 0) {
            let word = words.pop();
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > (svgRef.current.clientWidth / 2 - 15)) {
                line.pop();
                tspan.text(line.join(" "));
                line = [word];
                tspan = text.append("tspan")
                    .attr("x", textPositionX)
                    .attr("y", textPositionY)
                    .attr("dy", ++lineNumber * lineHeight)
                    .text(word);
            }
        }

        let midPositionY = textPositionY + lineNumber * lineHeight / 2;

        svg.append("path")
            .attr("id", `${GlyphList[i]['claim']}`)
            .attr("d", () => {
                const t = (GlyphList[i]['supports'] + GlyphList[i]['contradicts'] + 1) / (maxLengthOfList + 1);
                if (pos === 0) {
                    return `M${glyphPositionX},${midPositionY - t * lineNumber * lineHeight / 2} L${svgRef.current.clientWidth - 5},${midPositionY - t * lineNumber * lineHeight / 2} L${glyphPositionX},${midPositionY + t * lineNumber * lineHeight / 2} z`;
                } else {
                    return `M${glyphPositionX},${midPositionY - t * lineNumber * lineHeight / 2} L${svgRef.current.clientWidth / 2 - 5},${midPositionY - t * lineNumber * lineHeight / 2} L${glyphPositionX},${midPositionY + t * lineNumber * lineHeight / 2} z`;
                }
            })
            .attr("stroke", "black")
            .attr("fill", () => {
                if (GlyphList[i]['supports'] === 0) {
                    return "white"
                } else if (GlyphList[i]['contradicts'] === 0) {
                    return color_green(1)
                } else {
                    return color_green(GlyphList[i]['supports'] / (GlyphList[i]['supports'] + GlyphList[i]['contradicts']))
                }
            });

        svg.append("path")
            .attr("d", () => {
                const t = (GlyphList[i]['supports'] + GlyphList[i]['contradicts'] + 1) / (maxLengthOfList + 1);
                if (pos === 0) {
                    return `M${glyphPositionX},${midPositionY + t * lineNumber * lineHeight / 2} L${svgRef.current.clientWidth - 5},${midPositionY + t * lineNumber * lineHeight / 2} L${svgRef.current.clientWidth - 5},${midPositionY - t * lineNumber * lineHeight / 2} z`;
                } else {
                    return `M${glyphPositionX},${midPositionY + t * lineNumber * lineHeight / 2} L${svgRef.current.clientWidth / 2 - 5},${midPositionY + t * lineNumber * lineHeight / 2} L${svgRef.current.clientWidth / 2 - 5},${midPositionY - t * lineNumber * lineHeight / 2} z`;
                }
            })
            .attr("stroke", "black")
            .attr("fill", () => {
                if (GlyphList[i]['contradicts'] === 0) {
                    return "white"
                } else if (GlyphList[i]['supports'] === 0) {
                    return color_red(1)
                } else {
                    return color_red(GlyphList[i]['contradicts'] / (GlyphList[i]['supports'] + GlyphList[i]['contradicts']))
                }
            });



        textPositionY = textPositionY + 30 + lineNumber * lineHeight;
    }

    svg.attr("style", "height: -webkit-fill-available;").
        attr("style", `min-height: ${textPositionY + 5}`);

    return svg.node();
}

export default RenderGlyph;



