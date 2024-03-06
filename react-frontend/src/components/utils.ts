import { Margin } from "../types/margin";

export function getChildOrAppend<
    GElement extends d3.BaseType,
    PElement extends d3.BaseType
>(root: d3.Selection<PElement, any, any, any>, tag: string, className: string) {
    const node = root.selectAll(`${tag}.${className}`);

    node
        .data([tag])
        .enter()
        .append<GElement>(tag)
        .attr("class", className);

    return root.select<GElement>(`${tag}.${className}`);
}

export const DEFAULT_MARGIN = {
  top: 20,
  left: 40,
  bottom: 20,
  right: 20
}

export const getMargin = (margin?: Margin) => {
  if (!margin) return DEFAULT_MARGIN
  else return {...DEFAULT_MARGIN, ...margin}
}

export interface ChartStyle {
  width: number
  height: number
  margin?: Margin
}