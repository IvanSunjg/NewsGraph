import * as d3 from "d3";

function RenderLinks(linkContainerRef, svgLefts, svgRights, glyphData, leftNo, rightNo) {

    const leftData = glyphData[leftNo];

    const svg = d3.select(linkContainerRef.current);

    const svgRect = linkContainerRef.current.getBoundingClientRect();

    for (let i = 0; i < leftData.length; i++) {
        for (let j = 0; j < leftData[i].length; j++) {
            for (let m = 0; m < leftData[i][j]['supports_positions'].length; m++) {
                if (leftData[i][j]['supports_positions'][m]['paper_no'] === rightNo) {
                    const left = leftData[i][j]['supports_positions'][m];
                    const rightSvgRect = svgRights[left['paragraph']].current.getElementById(`${left['their_claim']}`).getBoundingClientRect();
                    const leftSvgRect = svgLefts[i].current.getElementById(`${leftData[i][j]['claim']}`).getBoundingClientRect();

                    const startX = leftSvgRect.right;
                    const startY = leftSvgRect.top + (leftSvgRect.height / 2);

                    const relativeStartX = startX - svgRect.left;
                    const relativeStartY = startY - svgRect.top;

                    const endX = rightSvgRect.left;
                    const endY = rightSvgRect.top + (rightSvgRect.height / 2);

                    const relativeEndX = endX - svgRect.left;
                    const relativeEndY = endY - svgRect.top;

                    let pathData;

                    if (Math.abs(relativeStartY - relativeEndY) > 6 * Math.abs(relativeStartX - relativeEndX)) {
                        pathData = `M ${relativeStartX},${relativeStartY} C ${2 * relativeEndX - relativeStartX},${relativeStartY} ${2 * relativeStartX - relativeEndX},${relativeEndY} ${relativeEndX},${relativeEndY}`;
                    } else {
                        pathData = `M ${relativeStartX},${relativeStartY} C ${relativeEndX},${relativeStartY} ${relativeStartX},${relativeEndY} ${relativeEndX},${relativeEndY}`;
                    }

                    const path = svg.append('path')
                        .attr('d', pathData)
                        .attr('stroke', 'lightgreen')
                        .attr('stroke-width', 3)
                        .attr('fill', 'none');

                    path.on('click', function (event) {
                        svg.selectAll('path')
                            .each(function () {
                                const strokeColor = d3.select(this).attr('stroke');
                                if (strokeColor === 'green') {
                                    d3.select(this).attr('stroke', 'lightgreen');
                                }
                            });
                        d3.select(this).attr('stroke', 'green');
                        const [clickX, clickY] = d3.pointer(event);
                        const distToStart = Math.sqrt(Math.pow(clickX - relativeStartX, 2) + Math.pow(clickY - relativeStartY, 2));
                        const distToEnd = Math.sqrt(Math.pow(clickX - relativeEndX, 2) + Math.pow(clickY - relativeEndY, 2));

                        if (distToStart < distToEnd) {
                            window.scrollTo({ top: rightSvgRect.top, behavior: 'smooth' });
                        } else {
                            window.scrollTo({ top: leftSvgRect.top, behavior: 'smooth' });
                        }
                    })
                }

                for (let n = 0; n < leftData[i][j]['contradicts_positions'].length; n++) {
                    if (leftData[i][j]['contradicts_positions'][n]['paper_no'] === rightNo) {
                        const left = leftData[i][j]['contradicts_positions'][n];
                        const rightSvgRect = svgRights[left['paragraph']].current.getElementById(`${left['their_claim']}`).getBoundingClientRect();
                        const leftSvgRect = svgLefts[i].current.getElementById(`${leftData[i][j]['claim']}`).getBoundingClientRect();

                        const startX = leftSvgRect.right;
                        const startY = leftSvgRect.top + (leftSvgRect.height / 2);

                        const relativeStartX = startX - svgRect.left;
                        const relativeStartY = startY - svgRect.top;

                        const endX = rightSvgRect.left;
                        const endY = rightSvgRect.top + (rightSvgRect.height / 2);

                        const relativeEndX = endX - svgRect.left;
                        const relativeEndY = endY - svgRect.top;

                        let pathData;

                        if (Math.abs(relativeStartY - relativeEndY) > 6 * Math.abs(relativeStartX - relativeEndX)) {
                            pathData = `M ${relativeStartX},${relativeStartY} C ${2 * relativeEndX - relativeStartX},${relativeStartY} ${2 * relativeStartX - relativeEndX},${relativeEndY} ${relativeEndX},${relativeEndY}`;
                        } else {
                            pathData = `M ${relativeStartX},${relativeStartY} C ${relativeEndX},${relativeStartY} ${relativeStartX},${relativeEndY} ${relativeEndX},${relativeEndY}`;
                        }

                        const path = svg.append('path')
                            .attr('d', pathData)
                            .attr('stroke', 'lightcoral')
                            .attr('stroke-width', 3)
                            .attr('fill', 'none');

                        path.on('click', function (event) {
                            svg.selectAll('path')
                                .each(function () {
                                    const strokeColor = d3.select(this).attr('stroke');
                                    if (strokeColor === 'red') {
                                        d3.select(this).attr('stroke', 'lightcoral');
                                    }
                                });
                            d3.select(this).attr('stroke', 'red');
                            const [clickX, clickY] = d3.pointer(event);
                            const distToStart = Math.sqrt(Math.pow(clickX - relativeStartX, 2) + Math.pow(clickY - relativeStartY, 2));
                            const distToEnd = Math.sqrt(Math.pow(clickX - relativeEndX, 2) + Math.pow(clickY - relativeEndY, 2));

                            if (distToStart < distToEnd) {
                                window.scrollTo({ top: rightSvgRect.top, behavior: 'smooth' });
                            } else {
                                window.scrollTo({ top: leftSvgRect.top, behavior: 'smooth' });
                            }
                        })
                    }
                }

            }
        }

        svg.on("click", function (event) {
            if (event.target === this) {
                svg.selectAll('path')
                    .each(function () {
                        const strokeColor = d3.select(this).attr('stroke');
                        if (strokeColor === 'red') {
                            d3.select(this).attr('stroke', 'lightcoral');
                        } else if (strokeColor === 'green') {
                            d3.select(this).attr('stroke', 'lightgreen');
                        }
                    });
            }
        });





    }
}
export default RenderLinks;