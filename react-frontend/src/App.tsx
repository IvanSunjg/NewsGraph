import * as React from 'react';
import { PaletteMode } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import AppAppBar from './components/AppAppBar';
import Hero from './components/Hero';
import Features from './components/Features';
import FAQ from './components/FAQ';
import getLPTheme from './getLPTheme';



export default function App() {
  const [mode, setMode] = React.useState<PaletteMode>('light');
  const [articleNo, setArticleNo] = React.useState<number>(-1);
  const [leftArticle, setLeftArticle] = React.useState<number>(-1);
  const [rightArticle, setRightArticle] = React.useState<number>(-1);
  const LPtheme = createTheme(getLPTheme(mode));

  const toggleColorMode = () => {
    setMode((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  React.useEffect(() => {
    if (articleNo !== -1) {
      console.log("Adding article:", articleNo);
      if (leftArticle === -1) {
        setLeftArticle(articleNo);
        console.log("Adding article on the left:", articleNo);
      } else if (rightArticle === -1) {
        setRightArticle(articleNo);
        console.log("Adding article on the right:", articleNo);
      }
    }
  }, [articleNo])

  return (
    <ThemeProvider theme={LPtheme}>
      <CssBaseline />
      {/* <AppAppBar mode={mode} toggleColorMode={toggleColorMode} /> */}
      <Hero addArticle={setArticleNo} />
      <Divider />
      <Box sx={{ bgcolor: 'background.default' }}>
        <Features leftNo={leftArticle} rightNo={rightArticle} setLefttNo={setLeftArticle} setRightNo={setRightArticle}/>
        <Divider />
        <FAQ />
        <Divider />
      </Box>
    </ThemeProvider>
  );
}
