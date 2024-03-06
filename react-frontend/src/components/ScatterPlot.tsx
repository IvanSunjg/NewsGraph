import { useEffect, createRef } from 'react'
import * as d3 from 'd3'
import { DataArray } from "../types/data";
import { ChartStyle, getChildOrAppend, getMargin } from './utils';
import './ScatterPlot.css'


interface ScatterPlotProp extends ChartStyle {
    data?: DataArray
}

const ScatterPlot = (props: ScatterPlotProp) => {
    const ref = createRef<SVGSVGElement>()
    const { data, ...style} = props
    useEffect(() => {
        const root = ref.current;
        if (data && root) {
            renderScatterPlot(root, data, style)
        }
    }, [props])

    return <div className="scatterPlot">
        <svg width={props.width} height={props.height} ref={ref} />
    </div>
}

/** 
 * Render the scatterplot
 * @param root the root SVG element
 * @param data the data for visualization
 * @param props the parameters of the scatterplot
*/
function renderScatterPlot(
    root: SVGElement | SVGGElement,
    data: DataArray,
    props: ChartStyle
) {
    const margin = getMargin(props.margin)
    const height = props.height - margin.top - margin.bottom
    const width = props.width - margin.left - margin.right

    const visRoot = d3.select(root)
    const base = getChildOrAppend<SVGGElement, SVGElement>(visRoot, "g", "base")
        .attr("transform", `translate(${margin.left}, ${margin.top})`)

    const xValues = data.map(d => d.X1)
    const x = d3.scaleLinear().domain([d3.min(xValues) || 0, d3.max(xValues) || 1]).range([0, width])
    const yValues = data.map(d => d.X2)
    const y = d3.scaleLinear().domain([d3.min(yValues) || 0, d3.max(yValues) || 1]).range([height, 0])
    const colors = d3.scaleOrdinal(["1", "2"], ["blue", "red"])

    base.selectAll("circle.dot")
        .data(data)
        .join<SVGCircleElement>(
            enter => enter.append("circle")
                .attr("class", "dot"),
            update => update,
            exit => exit.remove()
        )
        .attr("cx", d => x(d.X1))
        .attr("cy", d => y(d.X2))
        .attr("r", 5)
        .style("fill", d => colors(d.cluster) || "#fff")

    getChildOrAppend<SVGGElement, SVGGElement>(base, "g", "y-axis-base")
        .call(d3.axisLeft(y).ticks(4));

    getChildOrAppend<SVGGElement, SVGGElement>(base, "g", "x-axis-base")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x).ticks(5));
}


export default ScatterPlot;
