$ = require 'jquery'
React = require 'react'
ReactDOM = require 'react-dom'
videojs = require 'video.js'

Uploader = React.createFactory(require './Uploader')
AbstractView = require './AbstractView'

[_span, _input, _btn, _img, _h2, _hr, _div, _p, _video, _audio, _source,
 _h4, _h5] =\
  (React.createFactory(name) for name in\
  ['span', 'input', 'button', 'img', 'h2', 'hr', 'div', 'p', 'video', 'audio',
   'source', 'h4', 'h5'])

video_properties =
  className: 'video-js vjs-default-skin embed-responsive-item'
  preload: "auto"
  controls: true
  width: "640"
  height: "322"
  id: "video-el"
  key: "video-el"

audio_properties =
  className: 'embed-responsive-item'
  controls: true
  preload: 'auto'
  id: 'audio-preview'

preview_video = null
preview_audio = null

slider = React.createClass
  render: ->
    _div {className: 'col-md-4'},
      _div {className: 'panel panel-info'},
        _div {className: "panel-heading"},
          _h4 {className: "panel-title"}, "#{this.props.caption}"
        _div {className: "panel-body"},
          _input {id: this.props.id, type: 'range', className: 'sliderbar'}

slider = React.createFactory slider

new_view = React.createClass
  render: ->
    $$p = this.props

    sliders = (slider {key: id, id: 'dim' + id, caption: cap} for id, cap of {
      1: 'Dim1'
      2: 'Dim2'
      3: 'Dim3'
      4: 'Dim4'
      5: 'Dim5'
      6: 'Dim6'
      7: 'Dim7'
      8: 'Dim8'
      9: 'Dim9'
      10: 'Dim10'
    })

    _div {},
      _div {className: 'page-header'},
        _h2 {}, "How do you like your stuff?"
      Uploader {
        url: $$p.url
        evt_hnds: $$p.evt_hnds
        auto_upload: false
      }
      _hr {className: 'vnew'}
      _div {
        id: 'video-preview'
        className: "embed-responsive embed-responsive-16by9 mm-container"
      },
        _video video_properties
      _audio audio_properties
      _hr {}
      _div {className: "row"},
        sliders,
        _btn {type: "button", className: "btn btn-primary", id: "submit"},
          "Submit"

  componentDidMount: ->
    $$p = this.props

    $('#video-preview').hide()
    $('#audio-preview').hide()

    preview_audio = document.getElementById 'audio-preview'
    preview_video = videojs 'video-el'


module.exports = class VNew extends AbstractView
  constructor: (@url='/upload', anchor_id='upload') ->
    super '#' + anchor_id, anchor_id

    @evt_hnds = {
      addedfile: (file) ->
        $('#video-preview').show()

        if file.type.match /video/
          preview_video.src {
            src: window.URL.createObjectURL file
            type: file.type
          }
          preview_video.load()

        else
          $('#audio-preview').attr 'src', window.URL.createObjectURL(file)
          $('#audio-preview').attr 'type', file.type
          preview_audio.load()

          $(preview_audio).show()

      init: (dz) =>
        $('#submit').on 'click', =>
          data = new FormData()
          data.append 'file', dz.files[0]
          data.append 'dims', ($('#dim' + id).val() / 100.0 for id in [1..10])

          $.ajax {
            url: @url
            data: data
            processData: false
            contentType: false
            type: "POST"
            success: (data) =>
              alert 'Upload successful!'
              @hide()
              @render()
          }
    }

  render: ->
    super()

    ReactDOM.render React.createElement(new_view, {
      url: @url
      evt_hnds: @evt_hnds
    }), @anchor
