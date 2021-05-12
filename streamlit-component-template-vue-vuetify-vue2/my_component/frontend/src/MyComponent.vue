<template>
  <v-main class="wrapper" fill-height>
    <v-card id="highlighted-text-container" flat class="ml-2 mt-1" max-width="694" fill-height>
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
          <v-row class="mb-n3">
            <v-col cols="8">Claim</v-col>
            <v-col cols="4">Rating</v-col>
          </v-row>
          <v-row v-for="claim in args.labels[i].slice(0,5)" :key="claim['text']" class="my-n2">
            <v-col cols="8">{{claim.text}}</v-col>
            <v-col cols="4"><p class="truncate-overflow">{{claim.claimReview.length > 0 ? claim.claimReview[0].textualRating : ''}}</p></v-col>
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
    };
  },
  methods: {
    getClasses: function(i, sI) {
      if (i == 0 && i == this.args.labels[sI].slice(0,5).length -1) {
        return 'my-1'
      } else if (i == 0) {
        return 'mt-1'
      } else if (i == this.args.labels[sI].slice(0,5).length -1) {
        return 'mb-1'
      } else return ''
    }
  },
  updated() {
    this.$nextTick(function () {
    const element = document.getElementById('highlighted-text-container').getBoundingClientRect();
    const lastIndex = this.args.labels.length - 1;
    let additionalHeight = 0;
    if (Array.isArray(this.args.labels[lastIndex])) {
      additionalHeight = 500;
    }
    Streamlit.setFrameHeight(element.height + additionalHeight);
  })
  }
};
</script>
<style>
.truncate-overflow {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
}
</style>

