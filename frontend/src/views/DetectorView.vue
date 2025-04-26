<script setup>
import FallacyShort from '../components/FallacyShort.vue'
</script>

<template>
  <main>
    <div class="row" id="detector">
      <div class="col-8 offset-2">
        <p>FallaSee can detect logical fallacies in a sentence. Just write your sentence in the field below.</p>
        <textarea v-model="sentence" @input="countChar" placeholder="Type your sentence here." ></textarea>
        <p :class="{help: true, 'is-danger': remaining==0}"> {{instruction}} max characters</p>
        <!-- <p>{{ wordCount}} words</p> -->
      </div>
      <div class="col-8 offset-2 button">
        <button @click="pushFallacy(sentence)">
          detect fallacy
        </button>
      </div>
      <div class="row prediction ">
        <div class="col-md-8 offset-2" v-if="sentence_to_predict" >
          <div class="sentence">
            <h4> Sentence to predict:</h4>
            <div class="wrapper" >
              <p>{{ sentence_to_predict }}</p>
            </div>
          </div>
          <div class="result" v-if="predictionReady">
            <div v-for="(value, key) in resultList">
              <FallacyShort :label=value.fallacy :proba=value.proba :confidence = value.confidence></FallacyShort>
            </div>
            <p><i>We are very proud of our AI, but remember that having one sentence is rarely enough to decide with 100% certainty whether something is sound reasoning or not. Please be aware, our AI can only detect 5 logical fallacies. There are many more. AI can also make mistakes. Please check your text again!</i></p>
          </div>
          <div class="result" v-else>
            <h2>Loading ...</h2>
          </div>
        </div>
        <div class="col-10 offset-1 fallacy-list" v-if="list.length >0">
          <div class="heading">
            <h2> Previous results</h2>
            <button @click="clearLocalStorage" >  
              clear list
            </button>
          </div>
          <div class="table header">
            <div class="col-5">Sentence to predict</div>
            <div class="col-3">Result</div>
            <div class="col-2 tooltipWrapper">Confidence <span class="tooltipicon">?</span>
              <span class="tooltiptext">
                <h1>Confidence Levels</h1>
                <p><b>positive:</b> 90% – 100% <br>
                <b>very sure:</b> 70% – 90%<br>
                <b>sure:</b> 40% – 70%</p>
              </span></div>
            <div class="col-2">Probability</div>
          </div>
          <div class="table content" v-for="(value, key) in list">
            <div class="col-5 padding">{{value.sentence}}</div>
            <div class="col-3 listFallacy" :class="value.fallacy"><span></span>{{value.label}}</div>
            <div class="col-2">{{value.confidence}}</div>
            <div class="col-2">{{value.proba}}</div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<!-- https://heartbeat.comet.ml/deploying-a-text-classification-model-using-flask-and-vue-js-25b9aa7ff048 -->
<script>
import axios from 'axios'
axios.defaults.withCredentials = true;  // Ensure cookies are sent with requests

export default {
  data () {
    return {
      isAdHominem : false,
      isAuthority : false,
      isEmotion : false,
      isDilemma : false,
      isSlope : false,
      isNone : false,
      maxChar: 200,
      sentence : '',
      sentence_to_predict : null,
      data: '',
      resultList: [],
      list: [],
      predictionReady : false
    }
  },
  created () {
    this.getLocalStorage()
  },
  computed: {
    instruction() {  
      return this.count +' | '+ this.maxChar
    },
    remaining() {
      return this.maxChar-this.sentence.length;
    },
    count(){
      return this.sentence==''? 0: this.sentence.length
    }
  },
  methods: {
    countChar() {
        this.sentence = this.sentence.substr(0, this.maxChar)
    },
    getLocalStorage(){
      if (localStorage.getItem("FallacyList") != null) {
        this.data = localStorage.getItem('FallacyList')
        console.log('found local storage:', this.data)
        this.list = JSON.parse(this.data)
      } 
    },
    clearLocalStorage() {
      localStorage.clear()
      this.list = []
    },
    setPredictionArray(json_result) {
      let predictions = []
      for (var key in json_result){
        var value = json_result[key];
        predictions.push(value)
      }
      return predictions
    },
    getPrediction (data) {
      console.log('predict!')
      // await axios.get('http://localhost:5002/predict').then(
      //   result => {
          console.log("get Prediction:", data)
          this.resultList = []
          let predictions = this.setPredictionArray(data)
          let max = Math.max.apply(null, predictions)
          let position = predictions.indexOf(max)
          if (max >= 0.9) {
            let confidence = this.getConfidence(max)
            let item = {'fallacy': position, 'proba':max, 'confidence': confidence}
            this.resultList.push(item)
            console.log('show only one fallacy', max)
          }
          else if (max > 0.4) {
            let confidence = this.getConfidence(max)
            let item = {'fallacy': position, 'proba':max, 'confidence': confidence}
            this.resultList.push(item)
            let currentPreds = [...predictions];
            console.log('before:', currentPreds, predictions)
            currentPreds.splice(position, 1)
            console.log('after:', currentPreds, predictions)  
            let max2 =  Math.max.apply(null, currentPreds)
            let position2 = predictions.indexOf(max2)
            let item2 = {'fallacy': position2, 'proba':max2, 'confidence': 'chance'}
            this.resultList.push(item2)
            console.log('show more fallacies:', max, max2)
          }
          else {
            let item = {'fallacy': 6, 'proba':0, 'confidence': ''}
            this.resultList.push(item)
            console.log('show no fallacy')
          }
          console.log('resultList:', this.resultList)
          this.predictionReady = true
          if (max > 0.4) {this.setFallacyToLocalStorage(position, max, this.sentence)}
          this.sentence = ''
    },
    calculate(proba) {
      let proba_hundred = proba * 100
      return proba_hundred.toFixed(2) + ' %'
    },
    getLabel(fallacy) {
      if(fallacy == 0) { return 'Ad Hominem'}
      if(fallacy == 1) { return 'Appeal to Authority'}
      if(fallacy == 2) { return 'Appeal to Emotion'}
      if(fallacy == 3) { return 'False Dilemma'}
      if(fallacy == 4) { return 'No Fallacy'}
      if(fallacy == 5) { return 'Slippery Slope'}},
    getClass(fallacy) {
      if(fallacy == 0) { return 'adHominem'}
      if(fallacy == 1) { return 'authority'}
      if(fallacy == 2) { return 'emotion'}
      if(fallacy == 3) { return 'dilemma'}
      if(fallacy == 4) { return 'none'}
      if(fallacy == 5) { return 'slope'}},
    getConfidence(proba) {
      let confidence
      if (proba > 0.9){
        confidence = 'positive'
        return confidence
      }
      else if (proba > 0.7) {
        confidence = 'very sure'
        return confidence
      }
      else if (proba > 0.4) {
        confidence = 'sure'
        return confidence
      }
      else {
        confidence = 'need more context'
        return confidence
      }
      
    },
    setFallacyToLocalStorage(fallacy, proba, sentence){
      if (localStorage.getItem("FallacyList") != null) {
        this.data = localStorage.getItem('FallacyList')
        console.log('found local storage:', this.data)
        this.list = JSON.parse(this.data)
      } 
      let newEntry = {
        'sentence': sentence,
        'fallacy': this.getClass(fallacy),
        'label': this.getLabel(fallacy),
        'proba': this.calculate(proba),
        'confidence': this.getConfidence(proba),

      }
      this.list.unshift(newEntry)
      localStorage.setItem('FallacyList', JSON.stringify(this.list))
      console.log('Set local storage:', this.list)
      console.log('Get local storage:', localStorage.getItem('FallacyList'))
    },
    async pushFallacy () {
      this.predictionReady = false
      this.sentence_to_predict = this.sentence
      // this.setFallacyToLocalStorage(this.fallacy)
      await axios.post('http://localhost:5002/predict',
        { txt: this.sentence }, 
      )
      .then(res => {
        console.log('res push fallacy', res.data)
        this.getPrediction(res.data)
      })
      .catch(err => {
        console.log(err)
      })
    },
  }
  
}
</script>