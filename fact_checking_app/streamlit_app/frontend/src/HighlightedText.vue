<template>
  <v-main class="wrapper" fill-height>
    <v-card
      id="highlighted-text-container"
      flat
      class="ml-2 mt-1"
      max-width="694"
      fill-height
    >
      <span class="pb-0"
        >The sentences, containing potentially dubious claims, are highlighted
        accordingly:</span
      >
      <v-timeline class="ml-n15 pt-1" dense>
        <v-timeline-item class="pb-1" small color="red lighten-2"
          >False</v-timeline-item
        >
        <v-timeline-item class="pb-1" small color="deep-orange lighten-2">
          Mostly False
        </v-timeline-item>
        <v-timeline-item class="pb-1" small color="yellow lighten-2"
          >Mixture</v-timeline-item
        >
        <v-timeline-item class="pb-1" small color="lime lighten-2"
          >MostlyTrue</v-timeline-item
        >
        <v-timeline-item class="pb-1" small color="green lighten-2"
          >True</v-timeline-item
        >
        <v-timeline-item class="pb-3" small color="cyan lighten-2"
          >Missing info/Unclear</v-timeline-item
        >
      </v-timeline>
      <span v-for="(s, i) in args.sentences" :key="i">
        <span v-if="args.labels[i] == 0">{{ s }}</span>
        <v-tooltip v-else bottom>
          <template v-slot:activator="{ on, attrs }">
            <span
              style="border-radius: 3px;"
              :class="calculateColor(args.labels[i])"
              v-bind="attrs"
              v-on="on"
              >{{ s }}</span
            >
          </template>
          <span v-if="args.labels[i] === 1"
            >Model classified sentence as suspicious, but no relevant claims
            were found</span
          >
          <span v-else>
            <v-row class="mb-n3">
              <v-col cols="8">Claim</v-col>
              <v-col cols="4">Rating</v-col>
            </v-row>
            <v-row
              v-for="claim in args.labels[i].slice(0, 5)"
              :key="claim['text']"
              class="my-n2"
            >
              <v-col cols="8">{{ claim.text }}</v-col>
              <v-col cols="4"
                ><p class="truncate-overflow">
                  {{
                    claim.claimReview.length > 0
                      ? claim.claimReview[0].textualRating
                      : ""
                  }}
                </p></v-col
              >
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
  name: "HighlightedText",
  props: ["args"], // Arguments that are passed to the plugin in Python are accessible in props `args`. Here, we access the "name" arg.
  data() {
    return {
      trueValues: ["true", "accurate", "unbiased", "correct"],
      mostlyTrueValues: ["mostly true", "one pinocchio"],
      mixtureValues: ["mixture", "two pinocchios", "biased", "cherry-picking"],
      mostlyFalseValues: ["mostly false", "three pinocchios", "misleading"],
      falseValues: [
        "false",
        "four pinocchios",
        "inaccurate",
        "miscaptioned",
        "misattributed",
        "scam",
      ],
      colorMapping: {
        1: "red lighten-2",
        2: "deep-orange lighten-2",
        3: "yellow lighten-2",
        4: "lime lighten-2",
        5: "green lighten-2",
      },
    };
  },
  methods: {
    getClasses: function(i, sI) {
      if (i == 0 && i == this.args.labels[sI].slice(0, 5).length - 1) {
        return "my-1";
      } else if (i == 0) {
        return "mt-1";
      } else if (i == this.args.labels[sI].slice(0, 5).length - 1) {
        return "mb-1";
      } else return "";
    },
    calculateColor: function(reviews) {
      if (reviews == 1) {
        return "cyan lighten-4";
      } else {
        const ratings = [];
        reviews.forEach((review) => {
          if (review.claimReview.length > 0) {
            const rating = review.claimReview[0].textualRating;
            const numericalRating = this.determineRating(rating.toLowerCase());
            if (numericalRating) {
              ratings.push(numericalRating);
            }
          }
        });
        const average = Math.round(eval(ratings.join("+")) / ratings.length);
        return average ? this.colorMapping[average] : "cyan lighten-4";
      }
    },
    determineRating: function(textualRating) {
      if (this.mostlyTrueValues.find((v) => textualRating.includes(v))) {
        return 4;
      } else if (
        this.mostlyFalseValues.find((v) => textualRating.includes(v))
      ) {
        return 2;
      } else if (this.mixtureValues.find((v) => textualRating.includes(v))) {
        return 3;
      } else if (this.falseValues.find((v) => textualRating.includes(v))) {
        return 1;
      } else if (this.trueValues.find((v) => textualRating.includes(v))) {
        return 5;
      } else return null;
    },
  },
  updated() {
    this.$nextTick(function() {
      const element = document
        .getElementById("highlighted-text-container")
        .getBoundingClientRect();
      const lastIndex = this.args.labels.length - 1;
      let additionalHeight = 0;
      if (Array.isArray(this.args.labels[lastIndex])) {
        additionalHeight = 500;
      }
      Streamlit.setFrameHeight(element.height + additionalHeight);
    });
  },
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
.v-timeline::before {
  display: none;
}
.v-timeline-item__divider {
  min-width: 40px !important;
}
.v-timeline-item__body {
  margin-top: 3px !important;
  font-size: 14px !important;
}
</style>
