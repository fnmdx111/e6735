
ReactDOM = require 'react-dom'
$ = require 'jquery'

module.exports = class AbstractView
  constructor: (@show_hide_selector, @render_anchor_id) ->
    @shown = false

  refresh_refs: ->
    @anchor = document.getElementById @render_anchor_id
    @$el = $ @show_hide_selector

  render: ->
    @shown = true
    @$el?.removeClass 'invisible'

  unmount: ->
    ReactDOM.unmountComponentAtNode @anchor

  show: ->
    if not @shown
      @shown = true
      @$el?.removeClass 'invisible'

  hide: (unmount=true) ->
    if @shown
      @shown = false
      @$el?.addClass 'invisible'
      @unmount() if unmount

