import { useEffect, useState } from 'react';
import './App.css';
import { DataArray } from './types/data';
import DataChoiceComponent from './components/DataChoice';
import ScatterPlot from './components/ScatterPlot';
import { postPoints } from './router/resources/data';

function App() {

  const [exampleData, setExampleData] = useState<DataArray>();
  const [dataChoice, setDataChoice] = useState<string>();

  useEffect(() => {
    dataChoice && postPoints(dataChoice).then(exampleData => {
      setExampleData(exampleData);
    });
  }, [dataChoice]);

  function choiceMade(choice: string) {
    setDataChoice(choice);
  }

  return (
    <div className="App">
      <header className="App-header"> K-Means clustering
      </header>
      <DataChoiceComponent onChoiceMade={choiceMade} />
      <ScatterPlot width={1100} height={550} data={exampleData} />
    </div>
  )
}

export default App;
