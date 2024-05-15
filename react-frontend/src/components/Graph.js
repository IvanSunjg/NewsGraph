import * as d3 from "d3";

function bilink(root, type) {
    const map = new Map(root.leaves().map(d => [id(d), d]));
    for (const d of root.leaves()) {
        d.incoming = []
        if (type === 'support') {
            d.outgoing = d.data.supports.map(i => [d, map.get(i)]);
        } else {
            d.outgoing = d.data.contradicts.map(i => [d, map.get(i)]);
        }

    }
    for (const d of root.leaves()) {
        for (const o of d.outgoing) o[1].incoming.push(o);
    }
    return root;
}

function id(node) {
    return `${node.parent ? id(node.parent) + "." : ""}${node.data.name}`;
}

function RenderGraph(templateData, graphContainerRef, article, type, addArticle) {

    const colorin = "#00f";
    const colorout = "#f00";
    const colornone = "#ccc";

    const height = graphContainerRef.current.scrollHeight;
    const radius = height / 2.2;
    const tree = d3.cluster().size([2 * Math.PI, radius - 13]);
    let clicked = null;
    let forced = false;

    function handleArcClick(event, d) {
        addArticle(parseInt(d.name));
    }

    function handleArcMouseOver(event, d) {
        const darkerColor = d3.rgb(color(d.name)).darker(0.8);

        d3.select(this)
            .transition()
            .duration(200)
            .attr("fill", darkerColor);
    }

    function handleArcMouseOut(event, d) {
        d3.select(this)
            .transition()
            .duration(200)
            .attr("fill", color(d.name));
    }

    function handleTextClick(event, d) {
        if (clicked !== null) {
            forced = true;
            outed(event, clicked);
            clicked = null;
        }
        clicked = d;
        overed(event, d);
    }

    const svg = d3.select(graphContainerRef.current)
        .attr("width", height)
        .attr("height", height)
        .attr("viewBox", [-height / 2, -height / 2, height, height])
        .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif;");

    const root = tree(bilink(d3.hierarchy(templateData), type));

    const color = d3.scaleOrdinal(d3.schemePaired);

    const arcWidth = 13;
    const arcInnerRadius = radius - 13;
    const arcOuterRadius = arcInnerRadius + arcWidth;
    const arc = d3.arc()
        .innerRadius(arcInnerRadius)
        .outerRadius(arcOuterRadius)
        .startAngle((d) => d.start)
        .endAngle((d) => d.end);

    const leafGroups = d3.groups(root.leaves(), d => d.parent.data.name);

    const arcAngles = leafGroups.map(g => ({
        name: g[0],
        start: d3.min(g[1], d => d.x),
        end: d3.max(g[1], d => d.x)
    }));

    svg.selectAll(".arc")
        .data(arcAngles)
        .enter()
        .append("path")
        .attr("id", (d, i) => `arc_${i}`)
        .attr("d", (d) => arc({ start: d.start, end: d.end }))
        .attr("fill", d => color(d.name))
        .attr("stroke", d => color(d.name))
        .on("mouseover", handleArcMouseOver)
        .on("mouseout", handleArcMouseOut)
        .on("click", handleArcClick);

    svg.selectAll(".arcLabel")
        .data(arcAngles)
        .enter()
        .append("text")
        .attr("font-size", 12)
        .attr("font-family", "sans-serif")
        .attr("x", 13)
        .attr("dy", (d) => ((arcOuterRadius - arcInnerRadius) * 0.8))
        .append("textPath")
        .attr("class", "arcLabel")
        .attr("xlink:href", (d, i) => `#arc_${i}`)
        .text((d, i) => ((d.end - d.start) < (3 * Math.PI / 180)) ? "" : d.name);

    const line = d3.lineRadial()
        .curve(d3.curveBundle.beta(0.85))
        .radius(d => d.y)
        .angle(d => d.x);

    if (type === 'support') {
        const node = svg.append("g")
            .selectAll()
            .data(root.leaves())
            .join("g")
            .attr("transform", d => `rotate(${d.x * 180 / Math.PI - 90}) translate(${d.y},0)`)
            .append("text")
            .attr("dy", "0.31em")
            .attr("x", d => d.x < Math.PI ? 15 : -15)
            .attr("text-anchor", d => d.x < Math.PI ? "start" : "end")
            .attr("transform", d => d.x >= Math.PI ? "rotate(180)" : null)
            .text(d => d.data.name)
            .each(function (d) { d.text = this; })
            .on("mouseover", overed)
            .on("mouseout", outed)
            .on("click", handleTextClick)
            .call(text => text.append("title").text(d => `${id(d)}
            ${d.outgoing.length} entail
            ${d.incoming.length} entailed`));
    } else {
        const node = svg.append("g")
            .selectAll()
            .data(root.leaves())
            .join("g")
            .attr("transform", d => `rotate(${d.x * 180 / Math.PI - 90}) translate(${d.y},0)`)
            .append("text")
            .attr("dy", "0.31em")
            .attr("x", d => d.x < Math.PI ? 15 : -15)
            .attr("text-anchor", d => d.x < Math.PI ? "start" : "end")
            .attr("transform", d => d.x >= Math.PI ? "rotate(180)" : null)
            .text(d => d.data.name)
            .each(function (d) { d.text = this; })
            .on("mouseover", overed)
            .on("mouseout", outed)
            .on("click", handleTextClick)
            .call(text => text.append("title").text(d => `${id(d)}
            ${d.outgoing.length} contradicts
            ${d.incoming.length} contradicted`));
    }

    const link = svg.append("g")
        .attr("stroke", colornone)
        .attr("fill", "none")
        .selectAll("path")
        .data(root.leaves().flatMap(leaf => leaf.outgoing ? leaf.outgoing : []))
        .join("path")
        .style("mix-blend-mode", "multiply")
        .attr("d", ([i, o]) => {
            if (o.parent.data.name === String(article) || i.parent.data.name === String(article)) {
                return line(i.path(o));
            } else {
                return null;
            }
        })
        .each(function (d) { d.path = this; });


    function overed(event, d) {
        link.style("mix-blend-mode", null);
        d3.select(this).attr("font-weight", "bold");
        d3.selectAll(d.incoming.map(d => d.path)).attr("stroke", colorin).raise();
        d3.selectAll(d.incoming.map(([d]) => d.text)).attr("fill", colorin).attr("font-weight", "bold");
        d3.selectAll(d.outgoing.map(d => d.path)).attr("stroke", colorout).raise();
        d3.selectAll(d.outgoing.map(([, d]) => {
            if (d && d.text) {
                return d.text;
            } else {
                return null;
            }
        })).attr("fill", colorout).attr("font-weight", "bold");
    }

    function outed(event, d) {
        if (d !== clicked || forced) {
            if (clicked === null || forced) {
                link.style("mix-blend-mode", "multiply");
            }
            d3.select(d.text).attr("font-weight", null);
            d3.selectAll(d.incoming.map((d) => d.path)).attr("stroke", null);
            d3.selectAll(d.incoming.map(([d]) => d.text)).attr("fill", null).attr("font-weight", null);
            d3.selectAll(d.outgoing.map(d => d.path)).attr("stroke", null);
            d3.selectAll(d.outgoing.map(([, d]) => {
                if (d && d.text) {
                    return d.text;
                } else {
                    return null;
                }
            })).attr("fill", null).attr("font-weight", null);
            forced = false;
        }
    }

    d3.select(graphContainerRef.current)
        .on("click", function (event) {
            if (event.target === this) {
                if (clicked !== null) {
                    forced = true;
                    outed(event, clicked)
                    clicked = null;
                }
            }
        });

    return svg.node();

}

export default RenderGraph;