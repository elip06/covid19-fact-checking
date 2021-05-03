<template>
  <v-main class="wrapper" fill-height>
    <!-- 
      Show a button and some text.
      When the button is clicked, we'll increment our "numClicks" state
      variable, and send its new value back to Streamlit, where it'll
      be available to the Python program.
    -->
    <v-card flat class="ml-2 mt-1" max-width="694" fill-height>
      <span v-for="(s, i) in args.sentences" :key="i">
       <span v-if="args.labels[i]==0">{{s}}</span>
       <v-tooltip v-else bottom>
        <template v-slot:activator="{ on, attrs }">
         <span
          style="border-radius: 3px;"
          :class="args.labels[i]==1 ? 'orange lighten-4 m-1' : 'red lighten-4 m-1'"
          v-bind="attrs"
          v-on="on"
         >{{s}}</span>
        </template>
        <span v-if="args.labels[i] === 1">Model classified sentence as suspicious, but no relevant claims were found</span>
        <span v-else>
          <v-row>
            <v-col cols="9">Claim</v-col>
            <v-col cols="3">Rating</v-col>
          </v-row>
          <v-row v-for="(claim, index) in args.labels[i].slice(0,5)" :key="claim['text']" :class="getClasses(index, i)">
            <v-col cols="9">{{claim.text}}</v-col>
            <v-col cols="3">{{claim.claimReview.length > 0 ? claim.claimReview[0].textualRating : ''}}</v-col>
          </v-row>
        </span>
       </v-tooltip>
       <span class="ml-1" />
      </span>
    </v-card>
  </v-main>
</template>

<script>
import { Streamlit } from "streamlit-component-lib";

export default {
  name: "MyComponent",
  props: ["args"], // Arguments that are passed to the plugin in Python are accessible in props `args`. Here, we access the "name" arg.
  data() {
    return {
      numClicks: 0
    };
  },
  methods: {
    /** Click handler for our "Click Me!" button. */
    onClicked: function() {
      // Increment this.numClicks, and pass the new value back to
      // Streamlit via `Streamlit.setComponentValue`.
      this.numClicks++;
      Streamlit.setComponentValue(this.numClicks);
    },
    getClasses: function(i, sI) {
      if (i == 0 && i == this.args.labels[sI].slice(0,5).length -1) {
        return 'my-1'
      } else if (i == 0) {
        return 'mt-1'
      } else if (i == this.args.labels[sI].slice(0,5).length -1) {
        return 'mb-1'
      } else return ''
    }
  }
};
</script>

