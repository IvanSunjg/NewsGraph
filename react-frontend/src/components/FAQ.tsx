import * as React from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionDetails from '@mui/material/AccordionDetails';
import AccordionSummary from '@mui/material/AccordionSummary';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Link from '@mui/material/Link';
import Typography from '@mui/material/Typography';

import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

export default function FAQ() {
  const [expanded, setExpanded] = React.useState<string | false>(false);

  const handleChange =
    (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
      setExpanded(isExpanded ? panel : false);
    };

  return (
    <Container
      id="faq"
      sx={{
        pt: { xs: 4, sm: 12 },
        pb: { xs: 8, sm: 16 },
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: { xs: 3, sm: 6 },
      }}
    >
      <Typography
        component="h2"
        variant="h4"
        color="text.primary"
        sx={{
          width: { sm: '100%', md: '60%' },
          textAlign: { sm: 'left', md: 'center' },
        }}
      >
        Frequently asked questions
      </Typography>
      <Box sx={{ width: '100%' }}>
        <Accordion
          expanded={expanded === 'panel1'}
          onChange={handleChange('panel1')}
        >
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="panel1d-content"
            id="panel1d-header"
          >
            <Typography component="h3" variant="subtitle2">
              What does the Hierarchical Edge Bundling Graph stand for?
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography
              variant="body2"
              gutterBottom
              sx={{ maxWidth: { sm: '100%', md: '70%' } }}
            >
              Pagination Navigation Bar contains all the possible indices of
              the articles with previous, next, first and last buttons enabled.
              Two hierarchical edge bundling graphs for entailment graph on the 
              left and contradiction graph on the right. The graphs serve to visually 
              represent the volume and distribution of claims across the news 
              collection while also depicting the relationships at the sentence 
              level among the articles.
            </Typography>
          </AccordionDetails>
        </Accordion>
        <Accordion
          expanded={expanded === 'panel2'}
          onChange={handleChange('panel2')}
        >
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="panel2d-content"
            id="panel2d-header"
          >
            <Typography component="h3" variant="subtitle2">
              What does the Features section stand for?
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography
              variant="body2"
              gutterBottom
              sx={{ maxWidth: { sm: '100%', md: '70%' } }}
            >
              When a user selects two news articles—the focus article on the left and the 
              reference article on the right—the dashboard displays the original articles 
              along with all their corresponding extracted claims. Each claim is accompanied 
              by a visual indicator consisting of two triangles forming a rectangle with a diagonal 
              line from the bottom left to the top right. The rectangles have a uniform width, while 
              their heights vary based on the number of claims that support or contradict the claim from 
              other articles. At the top of the section, there are two delete buttons to delete the 
              corresponding news articles. A greater height indicates a higher number of supporting or 
              contradicting claims, suggesting the claim's potential controversy or influence. The triangles 
              within the rectangles are colored red or green, corresponding to the numbers of entailments and 
              contradictions, respectively. The darker the color, the greater the number of relationships it 
              possesses compared to the other claims within the article. A white color indicates the absence of 
              such relationships.
            </Typography>
          </AccordionDetails>
        </Accordion>
        <Accordion
          expanded={expanded === 'panel3'}
          onChange={handleChange('panel3')}
        >
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="panel3d-content"
            id="panel3d-header"
          >
            <Typography component="h3" variant="subtitle2">
              How can I approach to the developers?
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography
              variant="body2"
              gutterBottom
              sx={{ maxWidth: { sm: '100%', md: '70%' } }}
            >
              You can reach us by emailing <Link> jiugengsun@gmail.com </Link>.
            </Typography>
          </AccordionDetails>
        </Accordion>
      </Box>
    </Container>
  );
}
