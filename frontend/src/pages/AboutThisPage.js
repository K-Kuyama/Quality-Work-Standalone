import { useState } from 'react';
import AboutThisPanel from "../components/AboutThisPanel"
import TextDocArea from '../components/TextDocArea';

function AboutThisPage(){
    // ライセンス条項などを記載したファイルを選択肢て表示する

    const [text_name, setTextName] = useState('AboutQW.txt')

    return(
		<div className="app_page">
			<div className="w_sidebar">
				<div id="controls" className="controls">
					<AboutThisPanel handler={setTextName} />
				</div>
			</div>
			<div className="n_contents">
				<TextDocArea text_name={text_name} />
			</div>
		</div>
	)
}

export default AboutThisPage;