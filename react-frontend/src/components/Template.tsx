import * as React from 'react';
import Box from '@mui/material/Box';
import { alpha } from '@mui/material';
import axios from 'axios';
import RenderGraph from './Graph';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';

interface TemplateProps {
    article: number;
    addArticle: ( articleNo: number) => void;
}

const Template: React.FC<TemplateProps> = (props) => {

    const { article, addArticle } = props

    const backend_url: string = process.env.NODE_ENV === "production" ? `http://be.${window.location.hostname}/api/v1` : "http://localhost:8000/api/v1"

    const [templateData, setTemplateData] = React.useState<any>(null);
    const graphContainerRef_support = React.createRef<SVGSVGElement>();
    const graphContainerRef_contras = React.createRef<SVGSVGElement>();

    React.useEffect(() => {
        if (!templateData) {
            const fetchData = async () => {
                try {
                    axios({
                        method: 'get',
                        url: `${backend_url}/graph_data`
                    })
                        .then(response => {
                            setTemplateData(response.data)
                        })
                } catch (error) {
                    console.error('Error fetching data:', error);
                }
            };
            fetchData()
        }
    }, []);

    React.useEffect(() => {
        if (templateData && graphContainerRef_support.current && graphContainerRef_contras.current) {
            const svgElement_support = graphContainerRef_support.current;
            if (svgElement_support) {
                while (svgElement_support.firstChild) {
                    svgElement_support.removeChild(svgElement_support.firstChild);
                }
            }
            const svgElement_contras = graphContainerRef_contras.current;
            if (svgElement_contras) {
                while (svgElement_contras.firstChild) {
                    svgElement_contras.removeChild(svgElement_contras.firstChild);
                }
            }
            RenderGraph(templateData, graphContainerRef_support, article, 'support', addArticle)
            RenderGraph(templateData, graphContainerRef_contras, article, 'contradicts', addArticle)
        }
    }, [templateData, article]);

    return (
        <Container id="template" style={{minWidth : '100%'}}>
            <Grid container>
                <Grid item xs={12} md={6} sx={{pr: { sm: 1 }}}>
                    <Box
                        sx={(theme) => ({
                            mt: { xs: 3, sm: 6 },
                            alignSelf: 'center',
                            height: { xs: 200, sm: 850 },
                            width: '100%',
                            backgroundSize: 'cover',
                            borderRadius: '10px',
                            outline: '1px solid',
                            outlineColor:
                                theme.palette.mode === 'light'
                                    ? alpha('#BFCCD9', 0.5)
                                    : alpha('#9CCCFC', 0.1),
                            boxShadow:
                                theme.palette.mode === 'light'
                                    ? `0 0 12px 8px ${alpha('#9CCCFC', 0.2)}`
                                    : `0 0 24px 12px ${alpha('#033363', 0.2)}`,
                        })}
                    >
                        <svg ref={graphContainerRef_support} style={{ width: '100%', height: '100%' }} />
                    </Box>

                </Grid>
                <Grid item xs={12} md={6} sx={{pr: { sm: 1 }}}>
                    <Box
                        sx={(theme) => ({
                            mt: { xs: 3, sm: 6 },
                            alignSelf: 'center',
                            height: { xs: 200, sm: 850 },
                            width: '100%',
                            backgroundSize: 'cover',
                            borderRadius: '10px',
                            outline: '1px solid',
                            outlineColor:
                                theme.palette.mode === 'light'
                                    ? alpha('#BFCCD9', 0.5)
                                    : alpha('#9CCCFC', 0.1),
                            boxShadow:
                                theme.palette.mode === 'light'
                                    ? `0 0 12px 8px ${alpha('#9CCCFC', 0.2)}`
                                    : `0 0 24px 12px ${alpha('#033363', 0.2)}`,
                        })}
                    >
                        <svg ref={graphContainerRef_contras} style={{ width: '100%', height: '100%' }} />
                    </Box>
                </Grid>
            </Grid>

        </Container>
    )

}


export default Template;
