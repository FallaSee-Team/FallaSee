<script setup>

</script>

<template>
  <main>
    <div class="gameResultWrapper">
      <div class="gameResult" :class="[show ? 'start' : 'displayNone']">
       {{ result }}
      </div>
    </div>
    <div class="col-12 introduction">
      <div class="status">
        <p><b>Round: {{ round }}</b></p>
        <p><b>YOU: {{ points_user }}  | AI: {{ points_ai }} </b></p>
      </div>
      <div class=" row gameWrapper">
        <p>{{ txt }}</p>
      </div>
      <div class="row gameButtons">
        <h3>{{ moderation }}</h3>
        <div class=" col-2 buttonWrapper adHominem">
          <div class="choices">
            <div class="circleWrapper" v-if="user_adHominem">
              <span class="user"><p>YOU</p></span>
            </div>
            <div class="circleWrapper" v-if="ai_adHominem">
              <span class="ai"><p>AI</p></span>
            </div>
          </div>
          <button :class="{'right' : isRight_adHominem, 'wrong': isWrong_adHominem , 'disabled': isDisabled}" @click="check('adHominem')"  >Ad Hominem</button>
        </div>
        <div class=" col-2 buttonWrapper authority">
          <div class="choices">
            <div class="circleWrapper" v-if="user_authority">
              <span class="user"><p>YOU</p></span>
            </div>
            <div class="circleWrapper" v-if="ai_authority">
              <span class="ai"><p>AI</p></span>
            </div>
          </div>
          <button :class="{'right' : isRight_authority, 'wrong': isWrong_authority , 'disabled': isDisabled}" @click="check('authority')"  >Appeal To Authority</button>
        </div>
        <div class=" col-2 buttonWrapper emotion">
          <div class="choices">
            <div class="circleWrapper" v-if="user_emotion">
              <span class="user"><p>YOU</p></span>
            </div>
            <div class="circleWrapper" v-if="ai_emotion">
              <span class="ai"><p>AI</p></span>
            </div>
          </div>
          <button :class="{'right' : isRight_emotion, 'wrong': isWrong_emotion , 'disabled': isDisabled}" @click="check('emotion')" >Appeal To Emotion</button>
        </div>
        <div class=" col-2 buttonWrapper dilemma">
          <div class="choices">
            <div class="circleWrapper" v-if="user_dilemma">
              <span class="user"><p>YOU</p></span>
            </div>
            <div class="circleWrapper" v-if="ai_dilemma">
              <span class="ai"><p>AI</p></span>
            </div>
          </div>
          <button :class="{'right' : isRight_dilemma, 'wrong': isWrong_dilemma , 'disabled': isDisabled}" @click="check('dilemma')" >False Dilemma</button>
        </div>
        <div class=" col-2 buttonWrapper slope"> 
          <div class="choices">
            <div class="circleWrapper" v-if="user_slope">
              <span class="user"><p>YOU</p></span>
            </div>
            <div class="circleWrapper" v-if="ai_slope">
              <span class="ai"><p>AI</p></span>
            </div>
          </div>
          <button :class="{'right' : isRight_slope, 'wrong': isWrong_slope , 'disabled': isDisabled}" @click="check('slope')" >Slippery Slope</button>
        </div>
        <div class=" col-2 buttonWrapper none">
          <div class="choices">
            <div class="circleWrapper" v-if="user_none">
              <span class="user"><p>YOU</p></span>
            </div>
            <div class="circleWrapper" v-if="ai_none">
              <span class="ai"><p>AI</p></span>
            </div>
          </div>
          <button :class="{'right' : isRight_none, 'wrong': isWrong_none , 'disabled': isDisabled}" @click="check('none')" >No Fallacy</button>
        </div>
      </div>
      <div class="row next">
        <button @click="nextRound()" >Next</button>
      </div>
    </div>
  </main>
</template>

<script>
import axios from 'axios'

axios.defaults.withCredentials = true; 

import data from '../assets/definitions.json'
const delay = ms => new Promise(res => setTimeout(res, ms));

export default {
  data() {
    return{
      points_user: 0,
      points_ai: 0,
      round: 1,
      txt : '',
      solution : '',
      prediction: '',
      isDisabled : false,
      isRight_adHominem: false,
      isRight_authority: false,
      isRight_emotion: false,
      isRight_dilemma: false,
      isRight_slope: false,
      isRight_none: false,
      isWrong_adHominem: false,
      isWrong_authority: false,
      isWrong_emotion: false,
      isWrong_dilemma: false,
      isWrong_slope: false,
      isWrong_none: false,
      user_adHominem : false,
      user_authority : false,
      user_emotion : false,
      user_dilemma : false,
      user_none : false,
      user_slope : false,
      ai_adHominem : false,
      ai_authority : false,
      ai_emotion : false,
      ai_dilemma : false,
      ai_none : false,
      ai_slope : false,
      moderation : 'Choose the right fallacy',
      result: '',
      show: false
    }
  },
  created(){
    this.getRandom()
  },
  methods: {
    async getRandom(){
      let random = Math.floor(Math.random() *data.game.length);
      this.txt = data.game[random].example
      this.solution = data.game[random].label
      await axios.post('http://localhost:5002/predict',
        { txt: this.txt }, 
      )
      .then(res => {
        this.prediction = this.getPrediction(res.data)
        console.log('Set prediction:' ,this.prediction)
      })
      .catch(err => {
        console.log(err)
      })
    },
    async check(user) {
      let userWrong = false
      let aiWrong = false
      if (this.prediction != this.solution) {
        aiWrong = true
      }
      if (user != this.solution) {
        userWrong = true
      }
      await this.setClasses(user, userWrong, aiWrong)

      let current_result = ''
      
      if(user == this.solution) {
        this.points_user = this.points_user +1
        current_result = '+1'
        if (this.prediction != user) {
          this.points_user = this.points_user +1
          current_result = '+2'
        }
      }
      else {
        current_result = '+0'
      } 
      if (this.prediction == this.solution) {
        this.points_ai = this.points_ai+1
      }

      this.result = current_result
    },
    nextRound() {
      this.round = this.round + 1
      this.reset()
      this.getRandom()
    },
    getPrediction (data) {
      let predictions = this.setPredictionArray(data)
      let max = Math.max.apply(null, predictions)
      let position = predictions.indexOf(max)
      return this.getLabel(position)
    },
    getLabel(fallacy) {
      if(fallacy == 0) { return 'adHominem'}
      if(fallacy == 1) { return 'authority'}
      if(fallacy == 2) { return 'emotion'}
      if(fallacy == 3) { return 'dilemma'}
      if(fallacy == 4) { return 'none'}
      if(fallacy == 5) { return 'slope'}
    },
    setPredictionArray(json_result) {
      let predictions = []
      for (var key in json_result){
        var value = json_result[key];
        predictions.push(value)
      }
      return predictions
    },
    async setClasses(user, userWrong, aiWrong) {
      this.isDisabled = true
      this.moderation = 'You have chosen:'
      // User Icon
      if(user == 'adHominem') { this.user_adHominem = true }
      if(user == 'authority') { this.user_authority = true}
      if(user == 'emotion') { this.user_emotion = true}
      if(user == 'dilemma') { this.user_dilemma = true}
      if(user == 'none') { this.user_none = true}
      if(user == 'slope') { this.user_slope = true}
      await delay(1000);
      this.moderation = 'The AI has predicted...'
      let random = Math.floor((Math.random() * 1000)+1000);
      await delay(random);
      // AI Icon
      if(this.prediction == 'adHominem') { this.ai_adHominem = true}
      if(this.prediction == 'authority') { this.ai_authority = true}
      if(this.prediction == 'emotion') { this.ai_emotion = true}
      if(this.prediction == 'dilemma') { this.ai_dilemma = true}
      if(this.prediction == 'none') { this.ai_none = true}
      if(this.prediction == 'slope') { this.ai_slope = true}
      this.moderation = 'The correct answer is...'
      await delay(1000);
      // Button
      if(this.solution == 'adHominem') { this.isRight_adHominem = true}
      if(this.solution == 'authority') { this.isRight_authority = true}
      if(this.solution == 'emotion') { this.isRight_emotion = true}
      if(this.solution == 'dilemma') { this.isRight_dilemma = true}
      if(this.solution == 'none') { this.isRight_none = true}
      if(this.solution == 'slope') { this.isRight_slope = true}
      if(user == 'adHominem' & userWrong) {this.isWrong_adHominem=true} 
      if(user == 'authority' & userWrong) {this.isWrong_authority=true} 
      if(user == 'emotion' & userWrong) {this.isWrong_emotion=true} 
      if(user == 'dilemma' & userWrong) {this.isWrong_dilemma=true} 
      if(user == 'none' & userWrong) {this.isWrong_none=true} 
      if(user == 'slope' & userWrong) {this.isWrong_slope=true} 
      if(this.prediction == 'adHominem' & aiWrong) {this.isWrong_adHominem=true} 
      if(this.prediction == 'authority' & aiWrong) {this.isWrong_authority=true} 
      if(this.prediction == 'emotion' & aiWrong) {this.isWrong_emotion=true} 
      if(this.prediction == 'dilemma' & aiWrong) {this.isWrong_dilemma=true} 
      if(this.prediction == 'none' & aiWrong) {this.isWrong_none=true} 
      if(this.prediction == 'slope' & aiWrong) {this.isWrong_slope=true} 
      this.show = true
    },
    reset(){
      this.isDisabled = false,
      this.isRight_adHominem =false,
      this.isRight_authority =false,
      this.isRight_emotion =false,
      this.isRight_dilemma =false,
      this.isRight_slope =false,
      this.isRight_none =false,
      this.isWrong_adHominem =false,
      this.isWrong_authority =false,
      this.isWrong_emotion =false,
      this.isWrong_dilemma =false,
      this.isWrong_slope =false,
      this.isWrong_none =false,
      this.user_adHominem  =false,
      this.user_authority  =false,
      this.user_emotion  =false,
      this.user_dilemma  =false,
      this.user_none  =false,
      this.user_slope  =false,
      this.ai_adHominem  =false,
      this.ai_authority  =false,
      this.ai_emotion  =false,
      this.ai_dilemma  =false,
      this.ai_none  =false,
      this.ai_slope  =false,
      this.result = '',
      this.show = false,
      this.moderation = 'Choose the right fallacy'
    },
    
  }
}

</script>