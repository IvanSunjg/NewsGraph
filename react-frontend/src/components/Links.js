import * as d3 from "d3";

function RenderLinks(linkContainerRef, svgLefts, svgRights, glyphData, leftNo, rightNo) {

    const leftData = glyphData[leftNo];
    const rightDta = glyphData[rightNo];

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

                    


                    svg.append('line')
                        .attr('x1', relativeStartX)
                        .attr('y1', relativeStartY)
                        .attr('x2', relativeEndX)
                        .attr('y2', relativeEndY)
                        .attr('stroke', 'green');
                }
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


                    svg.append('line')
                        .attr('x1', relativeStartX)
                        .attr('y1', relativeStartY)
                        .attr('x2', relativeEndX)
                        .attr('y2', relativeEndY)
                        .attr('stroke', 'red');
                }
            }

        }
    }







}

export default RenderLinks;