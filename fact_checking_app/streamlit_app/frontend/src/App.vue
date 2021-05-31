<!-- 
  We bootstrap our Component to Streamlit with our scoped slot in the top-level App.
  This is where scoped slot passes Streamlit ;`args` data from itself to children HighlightedText.
  You should not have to edit this, but are free to do so :)
-->
<template>
  <v-app id="app">
    <WithStreamlitConnection style="height: 100%" v-slot="{ args }">
      <HighlightedText :args="args" />
    </WithStreamlitConnection>
  </v-app>
</template>

<script>
import HighlightedText from "./HighlightedText.vue";

// "withStreamlitConnection" is a scoped slot. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
import WithStreamlitConnection from "./streamlit/WithStreamlitConnection.vue";

export default {
  name: "App",
  components: { HighlightedText, WithStreamlitConnection }
};
</script>

<style>

#app {
  font-family: IBM Plex Sans, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
