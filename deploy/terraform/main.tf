terraform {
  backend "s3" {
    bucket = "legion-ci-configuration"
    key    = "terraform/state"
    region = "eu-central-1"
  }
}

variable "AWS_INSTANCE_TYPE" {}
variable "INSTANCE_NAME" {}
variable "ENV_NAME" {}
variable "AWS_REGION" {}
variable "AWS_SECURITY_GROUPS" {}
variable "AWS_IMAGE" {}
variable "AWS_KEY_NAME" {}
variable "AWS_SUBNET_ID" {}
variable "AWS_VOLUME_SIZE" {}
variable "WORKER_ASG_MAX_SIZE" {}
variable "WORKER_ASG_MIN_SIZE" {}
variable "WORKER_ASG_DESIRED_CAPACITY" {}
variable "WORKER_ASG_HC_GRACE_PERIOD" {}
variable "WORKER_ASG_HC_TYPE" {}


# Generate k8s admission token
resource "null_resource" "generate_k8s_token" {

  provisioner "local-exec" {
      command = "python -c 'import os, binascii; print(binascii.b2a_hex(os.urandom(15))[:6] + \".\" + binascii.b2a_hex(os.urandom(30))[:16])' > /tmp/${var.ENV_NAME}_token"
  }

  provisioner "local-exec" {
      when    = "destroy"
      command = "rm /tmp/${var.ENV_NAME}_token"
  }
}

data "local_file" "k8s_token" {
  depends_on = ["null_resource.generate_k8s_token"]
  filename = "/tmp/${var.ENV_NAME}_token"
}


provider "aws" {
    region = "${var.AWS_REGION}"
}

# Provision k8s master node
resource "aws_instance" "legion-k8s-master" {

    root_block_device {
        volume_type = "standard"
        volume_size = "${var.AWS_VOLUME_SIZE}"
    }

    volume_tags {
        Name = "${var.INSTANCE_NAME}-volume"
        EnvName = "${var.ENV_NAME}"
    }

    ami = "${var.AWS_IMAGE}"
    instance_type = "${var.AWS_INSTANCE_TYPE}"

    subnet_id = "${var.AWS_SUBNET_ID}"
    vpc_security_group_ids = ["${split(",", var.AWS_SECURITY_GROUPS)}"]
    associate_public_ip_address = true

    key_name = "${var.AWS_KEY_NAME}"
    user_data = "${data.template_file.k8s_master_user_data.rendered}"

    tags {
        Name    = "${var.INSTANCE_NAME}"
        EnvName = "${var.ENV_NAME}"
    }
}

resource "aws_eip" "legion-k8s-master-ip" {
    vpc = true
    instance = "${aws_instance.legion-k8s-master.id}"
}

data "template_file" "k8s_master_user_data" {
  template = <<-EOF
              #!/bin/bash
              mkdir -p /opt/k8s
              echo "${var.ENV_NAME}" > /opt/k8s/env_name
              echo "${data.local_file.k8s_token.content}" > /opt/k8s/token
              EOF
}


# k8s worker node ASG

resource "aws_launch_configuration" "legion-k8s-workers-lc" {
  name            = "${var.ENV_NAME}-k8s-workers-lc"
  image_id        = "${var.AWS_IMAGE}"
  instance_type   = "${var.AWS_INSTANCE_TYPE}"
  security_groups = ["${split(",", var.AWS_SECURITY_GROUPS)}"]
  key_name        = "${var.AWS_KEY_NAME}"
  user_data       = "${data.template_file.k8s_worker_user_data.rendered}"
}

data "template_file" "k8s_worker_user_data" {
  template = <<-EOF
              #!/bin/bash
              mkdir -p /opt/k8s
              echo "${var.ENV_NAME}" > /opt/k8s/env_name
              echo "${data.local_file.k8s_token.content}" > /opt/k8s/token
              echo "${aws_instance.legion-k8s-master.private_ip}" > /opt/k8s/k8s_master_ip
              EOF
}

resource "aws_autoscaling_group" "legion-k8s-workers-asg" {
  name                      = "${var.ENV_NAME}-k8s-workers-asg"
  max_size                  = "${var.WORKER_ASG_MAX_SIZE}"
  min_size                  = "${var.WORKER_ASG_MIN_SIZE}"
  health_check_grace_period = "${var.WORKER_ASG_HC_GRACE_PERIOD}"
  health_check_type         = "${var.WORKER_ASG_HC_TYPE}"
  desired_capacity          = "${var.WORKER_ASG_DESIRED_CAPACITY}"
  launch_configuration      = "${aws_launch_configuration.legion-k8s-workers-lc.name}"
  vpc_zone_identifier       = ["${var.AWS_SUBNET_ID}"]

  tag {
    key                 = "Name"
    value               = "${var.ENV_NAME}-k8s-worker"
    propagate_at_launch = true
  }
  tag {
    key                 = "EnvName"
    value               = "${var.ENV_NAME}"
    propagate_at_launch = true
  }
}

output "public_ip" {
  value = "${aws_eip.legion-k8s-master-ip.public_ip}"
}

output "private_ip" {
  value = "${aws_instance.legion-k8s-master.private_ip}"
}
