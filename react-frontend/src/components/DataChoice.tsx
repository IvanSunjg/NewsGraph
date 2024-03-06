import React from 'react';


class DataChoiceComponent extends React.Component<{ onChoiceMade: any }, { text: string }>{

  constructor(props: any) {
    super(props);
    this.state = { text: '' };
    this.handleChange = this.handleChange.bind(this);
    this.handleChoice = this.handleChoice.bind(this);
  }

  render() {
    return (
      <div>
        <label htmlFor="data-choice">
          Which dataset do you want to use? (moons, blobs, circles)
        </label>
        <input
          id="data-choice"
          onChange={this.handleChange}
          value={this.state.text}
        />
        <button onClick={this.handleChoice}>
          Confirm
        </button>
      </div>
    );
  }

  handleChange(e: any) {
    this.setState({ text: e.target.value });
  }

  handleChoice(e: any) {
    console.log('Previous state: ', this.state)
    this.props.onChoiceMade(this.state.text);
    this.setState({
      text: '',
    });
  }
}
export default DataChoiceComponent;