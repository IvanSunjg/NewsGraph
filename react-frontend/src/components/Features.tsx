import * as React from 'react';
import './Features.css';
import Button from '@mui/material/Button';
import DeleteIcon from '@mui/icons-material/Delete';
import Box from '@mui/material/Box';
import axios from 'axios';
import Card from '@mui/material/Card';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import Divider from '@mui/material/Divider';
import RenderGlyph from './Glyph';
import RenderLinks from './Links';


interface FeaturesProps {
  leftNo: number;
  rightNo: number;
  setLefttNo: (articleNo: number) => void;
  setRightNo: (articleNo: number) => void;
}

export default function Features(props: FeaturesProps) {

  const { leftNo, rightNo, setLefttNo, setRightNo } = props;

  const backend_url: string = process.env.NODE_ENV === "production" ? `http://be.${window.location.hostname}/api/v1` : "http://localhost:8000/api/v1"

  const [templateData, setTemplateData] = React.useState<any>(null);
  const [glyphData, setGlyphData] = React.useState<any>(null);
  const [svgRightRefs, setSvgRightRefs] = React.useState<Array<React.RefObject<SVGSVGElement>>>([]);
  const [svgLeftRefs, setSvgLeftRefs] = React.useState<Array<React.RefObject<SVGSVGElement>>>([]);
  const [filteredLeftStrings, setFilteredLeftStrings] = React.useState<Array<String>>([]);
  const [filteredRightStrings, setFilteredRightStrings] = React.useState<Array<String>>([]);
  const [leftGraph, setLeftGraph] = React.useState<boolean>(false);
  const [rightGraph, setRightGraph] = React.useState<boolean>(false);
  const linkContainerRef = React.createRef<SVGSVGElement>();

  React.useEffect(() => {
    if (!templateData) {
      const fetchData = async () => {
        try {
          axios({
            method: 'get',
            url: `${backend_url}/template_data`
          })
            .then(response => {
              setTemplateData(response.data)
            })
        } catch (error) {
          console.error('Error fetching data:', error);
        }

        try {
          axios({
            method: 'get',
            url: `${backend_url}/glyph_data`
          })
            .then(response => {
              setGlyphData(response.data)
            })
        } catch (error) {
          console.error('Error fetching data:', error);
        }
      };
      fetchData()
    }
  }, []);

  React.useEffect(() => {
    if (leftNo !== -1) {
      setFilteredLeftStrings(templateData[leftNo]['paragraphs'].filter((str: string) => str !== ""));
    } else {
      setSvgLeftRefs([]);
      setLeftGraph(false);
    }
  }, [leftNo]);

  React.useEffect(() => {
    const newSvgLeftRefs = Array.from({ length: filteredLeftStrings.length }, () => React.createRef<SVGSVGElement>());
    setSvgLeftRefs(newSvgLeftRefs);
  }, [filteredLeftStrings]);

  React.useEffect(() => {
    let maxLength = 0;
    for (let i = 0; i < svgLeftRefs.length; i++) {
      for (let j = 0; j < glyphData[leftNo][i].length; j++) {
        if (glyphData[leftNo][i][j]['supports'] + glyphData[leftNo][i][j]['contradicts'] > maxLength) {
          maxLength = glyphData[leftNo][i][j]['supports'] + glyphData[leftNo][i][j]['contradicts'];
        }
      }
    }
    for (let s = 0; s < svgLeftRefs.length; s++) {
      if (glyphData[leftNo][s].length !== 0) {
        RenderGlyph(glyphData[leftNo][s], svgLeftRefs[s], 0, maxLength);
      }
    }
    if (maxLength > 0) {
      setLeftGraph(true);
    }
  }, [svgLeftRefs]);

  React.useEffect(() => {
    if (rightNo !== -1) {
      setFilteredRightStrings(templateData[rightNo]['paragraphs'].filter((str: string) => str !== ""));
    } else {
      setSvgRightRefs([]);
      setRightGraph(false);
    }
  }, [rightNo]);

  React.useEffect(() => {
    const newSvgRightRefs = Array.from({ length: filteredRightStrings.length }, () => React.createRef<SVGSVGElement>());
    setSvgRightRefs(newSvgRightRefs);
  }, [filteredRightStrings]);

  React.useEffect(() => {
    let maxLength = 0;
    for (let i = 0; i < svgRightRefs.length; i++) {
      for (let j = 0; j < glyphData[rightNo][i].length; j++) {
        if (glyphData[rightNo][i][j]['supports'] + glyphData[rightNo][i][j]['contradicts'] > maxLength) {
          maxLength = glyphData[rightNo][i][j]['supports'] + glyphData[rightNo][i][j]['contradicts'];
        }
      }
    }
    for (let s = 0; s < svgRightRefs.length; s++) {
      if (glyphData[rightNo][s].length !== 0) {
        RenderGlyph(glyphData[rightNo][s], svgRightRefs[s], 1, maxLength);
      }
    }
    if (maxLength > 0) {
      setRightGraph(true);
    }
  }, [svgRightRefs]);

  React.useEffect(() => {
    if (rightGraph && leftGraph) {
      RenderLinks(linkContainerRef, svgLeftRefs, svgRightRefs, glyphData, leftNo, rightNo);
    } else {
      const svgElement_link = linkContainerRef.current;
      if (svgElement_link) {
        while (svgElement_link.firstChild) {
          svgElement_link.removeChild(svgElement_link.firstChild);
        }
      }
    }
  }, [rightGraph, leftGraph])

  return (
    <Container id="features" sx={{ pt: { xs: 4, sm: 8 }, pb: { xs: 8, sm: 16 } }} style={{ minWidth: '100%' }}>
      <Grid sx={{ pb: { sm: 1 } }} container justifyContent="space-between">
        <Grid item >
          <Button variant="outlined" onClick={() => setLefttNo(-1)} startIcon={<DeleteIcon />}>
            Delete
          </Button>
        </Grid>
        <Grid item >
        </Grid>
        <Grid item justifyContent="flex-start">
          <Button variant="outlined" onClick={() => setRightNo(-1)} startIcon={<DeleteIcon />}>
            Delete
          </Button>
        </Grid>
      </Grid>
      <div className="svg-container">
        <svg className='svg-link' ref={linkContainerRef} style={{ width: '100%', height: '100%' }} />
        <Grid container spacing={2} sx={{ display: 'flex', maxWidth: '100%', height: 'auto' }}>
          <Grid
            item
            xs={12}
            md={6}
            sx={{ display: { xs: 'none', sm: 'flex' }, width: '100%' }}
          >
            <Card
              variant="outlined"
              sx={{
                height: '100%',
                width: '100%',
                display: { xs: 'none', sm: 'flex' },
                pointerEvents: 'none',
              }}
            >
              <Box
                sx={{
                  marginLeft: '5%',
                  width: '90%',
                  minHeight: 500,
                  height: '100%',
                  backgroundSize: 'contain',
                }}
              >
                {leftNo !== -1 &&
                  <div>
                    <Typography component="h3" variant="subtitle2">
                      {templateData[leftNo]['title']}
                    </Typography>
                    <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
                      {svgLeftRefs.map((ref, index) => {
                        return (
                          <div>
                            <ListItem alignItems="flex-start" sx={{ width: '100%', minHeight: 'auto' }}>
                              <Grid container sx={{ height: "auto" }}>
                                <Grid item xs={8} >
                                  <Typography
                                    variant="body2"
                                    gutterBottom
                                    sx={{ maxWidth: '100%' }}
                                  >
                                    {filteredLeftStrings[index]}
                                  </Typography>
                                  <Divider component="li" />
                                </Grid>
                                <Grid item xs={4} sx={{ width: '100%', height: "auto" }}>
                                  <svg ref={ref} style={{ width: '100%', minHeight: "auto" }} />
                                </Grid>
                              </Grid>
                            </ListItem>
                          </div>
                        )
                      })}
                    </List>
                  </div>
                }
              </Box>
            </Card>
          </Grid>
          <Grid
            item
            xs={12}
            md={6}
            sx={{ display: { xs: 'none', sm: 'flex' }, width: '100%' }}
          >
            <Card
              variant="outlined"
              sx={{
                height: '100%',
                width: '100%',
                display: { xs: 'none', sm: 'flex' },
                pointerEvents: 'none',
              }}
            >
              <Box
                sx={{
                  marginLeft: 'auto',
                  marginRight: '5%',
                  width: "90%",
                  minHeight: 500,
                  height: '100%',
                  backgroundSize: 'contain',
                }}
              >
                {rightNo !== -1 &&
                  <div>
                    <Typography component="h3" variant="subtitle2">
                      {templateData[rightNo]['title']}
                    </Typography>
                    <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
                      {svgRightRefs.map((ref, index) => (
                        <div>
                          <ListItem alignItems="flex-start" sx={{ width: '100%' }}>
                            <Grid container sx={{ height: "100%" }}>
                              <Grid item xs={4}>
                                <svg key={index} ref={ref} style={{ width: '100%' }} />
                              </Grid>
                              <Grid item xs={8} >
                                <Typography
                                  variant="body2"
                                  gutterBottom
                                  sx={{ maxWidth: '100%' }}
                                >
                                  {filteredRightStrings[index]}
                                </Typography>
                                <Divider component="li" />
                              </Grid>
                            </Grid>
                          </ListItem>
                        </div>
                      ))}
                    </List>
                  </div>
                }
              </Box>
            </Card>
          </Grid>
        </Grid>
      </div>
    </Container>
  );
}
