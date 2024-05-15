import { alpha } from '@mui/material';
import * as React from 'react';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Template from './Template';
import Pagination from '@mui/material/Pagination';

interface HeroPorps{
  addArticle: (articleNo: number) => void;
}

export default function Hero ({ addArticle }: HeroPorps) {

  const [article, setArticle] = React.useState(1);
  const handleChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setArticle(value);
  };

  return (
    <Box sx={{ pb: { xs: 8, sm: 12 } }}>
      <Box
        id="hero"
        sx={(theme) => ({
          width: '100%',
          backgroundImage:
            theme.palette.mode === 'light'
              ? 'linear-gradient(180deg, #CEE5FD, #FFF)'
              : `linear-gradient(#02294F, ${alpha('#090E10', 0.0)})`,
          backgroundSize: '100% 20%',
          backgroundRepeat: 'no-repeat'
        })}
      >
        <Container
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            pt: { xs: 14, sm: 20 },

          }}
        >
          <Stack spacing={2} useFlexGap sx={{ width: { xs: '100%', sm: '70%' } }}>
            <Typography
              variant="h1"
              sx={{
                display: 'flex',
                flexDirection: { xs: 'column', md: 'row' },
                alignSelf: 'center',
                textAlign: 'center',
                fontSize: 'clamp(3.5rem, 10vw, 4rem)',
              }}
            >
              News Collection&nbsp;
              <Typography
                component="span"
                variant="h1"
                sx={{
                  fontSize: 'clamp(3rem, 10vw, 4rem)',
                  color: (theme) =>
                    theme.palette.mode === 'light' ? 'primary.main' : 'primary.light',
                }}
              >
                Graph
              </Typography>
            </Typography>
          </Stack>
          <Box sx={{ width: 500 }}>
            <Pagination shape="rounded" page={article} onChange={handleChange} count={21} defaultPage={1} siblingCount={1} boundaryCount={2} showFirstButton showLastButton />
          </Box>
        </Container>

      </Box>
      <Template article={article} addArticle={addArticle}/>
    </Box>

  );
}
